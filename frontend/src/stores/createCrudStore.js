import { defineStore } from 'pinia'

/**
 * Factory that creates a Pinia store with standard CRUD actions.
 *
 * @param {string} id - Pinia store id.
 * @param {object} api - API functions: { list, retrieve, create, update, delete }.
 * @param {object} [options]
 * @param {object} [options.extraActions] - Additional actions merged into the store.
 * @param {object} [options.extraState] - Additional state properties.
 * @returns {import('pinia').StoreDefinition}
 */
export function createCrudStore(id, api, options = {}) {
  const { extraActions = {}, extraState = {} } = options

  const _builtInActions = [
    'fetchList', 'fetchCount', 'fetchDetail',
    'create', 'update', 'remove',
    'clearCurrent', 'clearItems',
  ]
  for (const key of Object.keys(extraActions)) {
    if (_builtInActions.includes(key)) {
      throw new Error(`createCrudStore("${id}"): extraAction "${key}" collides with a built-in action`)
    }
  }

  return defineStore(id, {
    state: () => ({
      items: [],
      currentItem: null,
      loading: false,
      error: null,
      ...extraState,
    }),
    actions: {
      async fetchList(params) {
        this.loading = true
        this.error = null
        try {
          const { data } = await api.list(params)
          this.items = data.results || []
          return data
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
        }
      },

      async fetchCount(params) {
        try {
          const { data } = await api.list({ ...params, page_size: 1 })
          return data.count
        } catch (e) {
          this.error = e.message
          throw e
        }
      },

      async fetchDetail(id, options = {}) {
        this.loading = true
        this.error = null
        let cancelled = false
        try {
          const { data } = await api.retrieve(id, { signal: options.signal })
          this.currentItem = data
          return data
        } catch (e) {
          if (e.code === 'ERR_CANCELED') {
            cancelled = true
            return
          }
          this.error = e.message
          throw e
        } finally {
          if (!cancelled) this.loading = false
        }
      },

      async create(payload) {
        this.loading = true
        this.error = null
        try {
          const { data } = await api.create(payload)
          return data
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
        }
      },

      async update(id, payload) {
        this.loading = true
        this.error = null
        try {
          const { data } = await api.update(id, payload)
          this.currentItem = data
          return data
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
        }
      },

      async remove(id) {
        this.loading = true
        this.error = null
        try {
          await api.delete(id)
          if (this.currentItem?.id === id) this.currentItem = null
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
        }
      },

      clearCurrent() {
        this.currentItem = null
      },

      clearItems() {
        this.items = []
      },

      ...extraActions,
    },
  })
}
