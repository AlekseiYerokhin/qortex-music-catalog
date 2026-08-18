import { onMounted, onUnmounted, ref } from 'vue'
import { useQuasar } from 'quasar'

/**
 * Composable that encapsulates server-side paginated table logic:
 * fetchTable, onRequest, onSearch (debounced), confirmDelete (with
 * last-item-on-page correction), and automatic timer cleanup on unmount.
 *
 * @param {object} store - A store created by createCrudStore.
 * @param {object} options
 * @param {string} [options.defaultSort='name'] - Default sort field.
 * @param {string} [options.entityName='Item'] - Human-readable entity name for dialogs.
 * @param {function|string} [options.deleteMessage] - Message or function(item) => string.
 */
export function useResourceTable(store, options = {}) {
  const {
    defaultSort = 'name',
    entityName = 'Item',
    deleteMessage,
  } = options

  const $q = useQuasar()
  const search = ref('')
  const tableError = ref(null)
  const pagination = ref({
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
    sortBy: defaultSort,
    descending: false,
  })

  let searchTimer = null

  async function fetchTable() {
    tableError.value = null
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.rowsPerPage,
    }
    if (search.value) params.search = search.value
    if (pagination.value.sortBy) {
      params.ordering = pagination.value.descending
        ? `-${pagination.value.sortBy}`
        : pagination.value.sortBy
    }
    try {
      const data = await store.fetchList(params)
      pagination.value.rowsNumber = data.count
    } catch (e) {
      tableError.value = e.message
    }
  }

  function onRequest(props) {
    pagination.value.page = props.pagination.page
    pagination.value.rowsPerPage = props.pagination.rowsPerPage
    pagination.value.sortBy = props.pagination.sortBy
    pagination.value.descending = props.pagination.descending
    fetchTable()
  }

  function onSearch() {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      pagination.value.page = 1
      fetchTable()
    }, 300)
  }

  function confirmDelete(item) {
    const message =
      typeof deleteMessage === 'function'
        ? deleteMessage(item)
        : deleteMessage || `Are you sure you want to delete "${item.name || item.title}"?`

    $q.dialog({
      title: `Delete ${entityName}`,
      message,
      cancel: true,
      persistent: true,
      ok: { label: 'Delete', color: 'negative', unelevated: true },
    }).onOk(async () => {
      try {
        await store.remove(item.id)
        $q.notify({ type: 'positive', message: `${entityName} deleted` })
        const remaining = pagination.value.rowsNumber - 1
        const maxPage = Math.max(
          1,
          Math.ceil(remaining / pagination.value.rowsPerPage)
        )
        if (pagination.value.page > maxPage) {
          pagination.value.page = maxPage
        }
        fetchTable()
      } catch {
        /* handled by interceptor */
      }
    })
  }

  onMounted(fetchTable)
  onUnmounted(() => clearTimeout(searchTimer))

  return { search, pagination, tableError, fetchTable, onRequest, onSearch, confirmDelete }
}
