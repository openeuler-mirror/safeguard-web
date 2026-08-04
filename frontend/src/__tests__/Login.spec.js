import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Login from '@/views/Login.vue'

// 模拟 Vuex 和 Router
const mockLogin = vi.fn()
const mockPush = vi.fn()

vi.mock('vuex', () => ({
  useStore: () => ({
    dispatch: mockLogin
  }),
  mapActions: () => ({
    login: mockLogin
  })
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({}),
  RouterLink: { template: '<a><slot /></a>' }
}))

describe('Login 页面测试', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Login, {
      global: {
        mocks: {
          $store: {
            dispatch: mockLogin
          },
          $router: {
            push: mockPush
          }
        },
        stubs: {
          RouterLink: true
        }
      }
    })
  }

})
