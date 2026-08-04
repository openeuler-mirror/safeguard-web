import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Profile from '@/views/Profile.vue'
import { updateMe } from '@/api/auth'

// 模拟 API 模块
vi.mock('@/api/auth')

const mockPush = vi.fn()
const mockLogout = vi.fn()
const mockFetchUser = vi.fn()

vi.mock('vuex', () => ({
  useStore: () => ({}),
  mapState: () => ({
    user: {
      user: 'testuser',
      nickname: 'Test User',
      phone: '13800138000',
      email: 'test@example.com',
      enable: 1
    }
  }),
  mapActions: () => ({
    logout: mockLogout,
    fetchUser: mockFetchUser
  })
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({})
}))

describe('Profile 页面测试', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockLogout.mockReset()
    mockFetchUser.mockReset()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Profile, {
      global: {
        mocks: {
          $store: {
            state: {
              auth: {
                user: {
                  user: 'testuser',
                  nickname: 'Test User',
                  phone: '13800138000',
                  email: 'test@example.com',
                  enable: 1
                }
              }
            }
          },
          $router: {
            push: mockPush
          }
        },
        stubs: {}
      }
    })
  }

})
