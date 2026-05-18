import { flushPromises } from '@vue/test-utils'

export async function waitForUpdate(wrapper) {
  await flushPromises()
  await wrapper.vm.$nextTick()
}
