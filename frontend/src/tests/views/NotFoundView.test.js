import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { QLayout, QPageContainer } from 'quasar'
import NotFoundView from '../../views/NotFoundView.vue'

describe('NotFoundView', () => {
  it('renders content (not blank) when inside QLayout', () => {
    const wrapper = mount({
      components: { QLayout, QPageContainer, NotFoundView },
      template: `
        <q-layout>
          <q-page-container>
            <not-found-view />
          </q-page-container>
        </q-layout>
      `,
    })
    expect(wrapper.text()).toContain('404')
    expect(wrapper.text()).toContain("doesn't exist")
  })
})
