import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import Profile from '@/views/Profile.vue'

vi.mock('@/api/auth')

const mockUser = {
  user: 'testuser',
  nickname: 'Test User',
  phone: '13800138000',
  email: 'test@example.com',
  enable: 1
}

describe('Profile 页面测试', () => {
  let wrapper
  let store

  beforeEach(() => {
    vi.clearAllMocks()
    store = createStore({
      modules: {
        auth: {
          namespaced: true,
          state: {
            user: mockUser,
            isAuthenticated: true,
            menus: []
          },
          getters: {
            user: (state) => state.user,
            isAuthenticated: (state) => state.isAuthenticated
          },
          actions: {
            logout: vi.fn(),
            fetchUser: vi.fn()
          }
        }
      }
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Profile, {
      global: {
        plugins: [store],
        stubs: {
          'router-link': true
        },
        mocks: {
          $router: {
            push: vi.fn()
          }
        }
      }
    })
  }

  describe('页面渲染', () => {
    it('应渲染个人中心页面', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.profile-container').exists()).toBe(true)
      expect(wrapper.find('.profile-box').exists()).toBe(true)
    })

    it('应显示"个人中心"标题', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('个人中心')
    })
  })
})
