import { describe, it, expect, vi, beforeEach, afterEach, fakeTimers } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Register from '@/views/Register.vue'
import { createUser, sendVerificationCode, verifyCode } from '@/api/auth'

// 模拟 API 模块
vi.mock('@/api/auth')

const mockPush = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({}),
  RouterLink: { template: '<a><slot /></a>' }
}))

describe('Register 页面测试', () => {
  let wrapper
  let clock

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    vi.useFakeTimers()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.useRealTimers()
  })

  const createWrapper = () => {
    return mount(Register, {
      global: {
        mocks: {
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
