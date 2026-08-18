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
        const { data } = await api.list({ ...params, page_size: 1 })
        return data.count
      },

      async fetchDetail(id) {
        this.loading = true
        this.error = null
        try {
          const { data } = await api.retrieve(id)
          this.currentItem = data
          return data
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
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
