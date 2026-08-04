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

  describe('页面初始状态', () => {
    it('应渲染个人中心页面', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.profile-container').exists()).toBe(true)
      expect(wrapper.find('.profile-box').exists()).toBe(true)
    })

    it('应显示"个人中心"标题', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('个人中心')
    })

    it('初始 editing 状态应为 false', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.editing).toBe(false)
    })

    it('初始 message 状态应为空', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.message).toBe('')
    })
  })

  describe('用户信息显示', () => {
    it('应显示用户名', async () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('用户名：')
      expect(wrapper.text()).toContain('testuser')
    })

    it('应显示昵称', async () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('昵称：')
      expect(wrapper.text()).toContain('Test User')
    })

    it('应显示手机号', async () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('手机号：')
      expect(wrapper.text()).toContain('13800138000')
    })

    it('应显示邮箱', async () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('邮箱：')
      expect(wrapper.text()).toContain('test@example.com')
    })

    it('应显示状态', async () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('状态：')
    })

    it('用户状态为正常时显示绿色', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.status-active').exists()).toBe(true)
      expect(wrapper.find('.status-active').text()).toBe('正常')
    })

    it('用户状态为禁用时显示红色', async () => {
      wrapper = mount(Profile, {
        global: {
          mocks: {
            $store: {
              state: {
                auth: {
                  user: {
                    user: 'testuser',
                    nickname: 'Test User',
                    phone: '',
                    email: '',
                    enable: 0
                  }
                }
              }
            },
            $router: {
              push: mockPush
            }
          }
        }
      })

      expect(wrapper.find('.status-disabled').exists()).toBe(true)
      expect(wrapper.find('.status-disabled').text()).toBe('已禁用')
    })

    it('手机号为空时显示"-"', async () => {
      wrapper = mount(Profile, {
        global: {
          mocks: {
            $store: {
              state: {
                auth: {
                  user: {
                    user: 'testuser',
                    nickname: 'Test User',
                    phone: '',
                    email: 'test@example.com',
                    enable: 1
                  }
                }
              }
            },
            $router: {
              push: mockPush
            }
          }
        }
      })

      expect(wrapper.text()).toContain('-')
    })

    it('邮箱为空时显示"-"', async () => {
      wrapper = mount(Profile, {
        global: {
          mocks: {
            $store: {
              state: {
                auth: {
                  user: {
                    user: 'testuser',
                    nickname: 'Test User',
                    phone: '13800138000',
                    email: '',
                    enable: 1
                  }
                }
              }
            },
            $router: {
              push: mockPush
            }
          }
        }
      })

      expect(wrapper.text()).toContain('-')
    })
  })

  describe('编辑模式', () => {
    it('点击编辑信息按钮进入编辑模式', async () => {
      wrapper = createWrapper()

      await wrapper.find('button').trigger('click')

      expect(wrapper.vm.editing).toBe(true)
    })

    it('进入编辑模式时表单数据从用户信息初始化', async () => {
      wrapper = createWrapper()

      await wrapper.find('button').trigger('click')

      expect(wrapper.vm.form.nickname).toBe('Test User')
      expect(wrapper.vm.form.phone).toBe('13800138000')
      expect(wrapper.vm.form.email).toBe('test@example.com')
    })

    it('进入编辑模式时清空消息', async () => {
      wrapper = createWrapper()
      wrapper.vm.message = '之前的消息'

      await wrapper.find('button').trigger('click')

      expect(wrapper.vm.message).toBe('')
    })

    it('编辑模式下显示输入框而非文本', async () => {
      wrapper = createWrapper()

      await wrapper.find('button').trigger('click')
      await flushPromises()

      expect(wrapper.findAll('.edit-input').length).toBe(3)
    })

    it('编辑模式下显示取消和保存按钮', async () => {
      wrapper = createWrapper()

      await wrapper.find('button').trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('取消')
      expect(wrapper.text()).toContain('保存')
    })

    it('点击取消按钮退出编辑模式', async () => {
      wrapper = createWrapper()

      await wrapper.find('button').trigger('click')
      await flushPromises()
      await wrapper.findAll('button')[0].trigger('click')

      expect(wrapper.vm.editing).toBe(false)
    })

    it('点击取消按钮清空消息', async () => {
      wrapper = createWrapper()

      await wrapper.find('button').trigger('click')
      await flushPromises()
      wrapper.vm.message = '测试消息'
      await wrapper.vm.cancelEdit()

      expect(wrapper.vm.message).toBe('')
    })
  })

})
