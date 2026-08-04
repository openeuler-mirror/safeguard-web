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

  describe('页面初始状态', () => {
    it('应渲染登录表单', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.login-container').exists()).toBe(true)
      expect(wrapper.find('.login-box').exists()).toBe(true)
    })

    it('应显示"用户登录"标题', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('用户登录')
    })

    it('应有用户名输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#username').exists()).toBe(true)
    })

    it('应有密码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#password').exists()).toBe(true)
    })

    it('应有登录按钮', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').text()).toBe('登录')
    })

    it('初始 loading 状态应为 false', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(false)
    })

    it('初始 error 状态应为空', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.error).toBe('')
    })
  })

  describe('表单数据绑定', () => {
    it('v-model 正确绑定用户名', async () => {
      wrapper = createWrapper()
      const usernameInput = wrapper.find('#username')

      await usernameInput.setValue('testuser')

      expect(wrapper.vm.form.username).toBe('testuser')
    })

    it('v-model 正确绑定密码', async () => {
      wrapper = createWrapper()
      const passwordInput = wrapper.find('#password')

      await passwordInput.setValue('testpass')

      expect(wrapper.vm.form.password).toBe('testpass')
    })
  })

  describe('登录成功流程', () => {
    it('点击登录按钮调用 login action', async () => {
      wrapper = createWrapper()
      mockLogin.mockResolvedValue({ success: true })

      const usernameInput = wrapper.find('#username')
      const passwordInput = wrapper.find('#password')
      await usernameInput.setValue('testuser')
      await passwordInput.setValue('testpass')

      await wrapper.find('form').trigger('submit.prevent')

      expect(mockLogin).toHaveBeenCalledWith('auth/login', { username: 'testuser', password: 'testpass' })
    })

    it('登录成功后跳转到 dashboard', async () => {
      wrapper = createWrapper()
      mockLogin.mockResolvedValue({ success: true })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      await wrapper.vm.handleLogin()
      await flushPromises()

      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })

    it('登录过程中显示 loading 状态', async () => {
      wrapper = createWrapper()
      let resolveLogin
      mockLogin.mockImplementation(() => {
        return new Promise(resolve => {
          resolveLogin = () => resolve({ success: true })
        })
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      const loginPromise = wrapper.vm.handleLogin()

      expect(wrapper.vm.loading).toBe(true)

      resolveLogin()
      await loginPromise
      await flushPromises()

      expect(wrapper.vm.loading).toBe(false)
    })

    it('登录过程中按钮显示"登录中..."', async () => {
      wrapper = createWrapper()
      let resolveLogin
      mockLogin.mockImplementation(() => {
        return new Promise(resolve => {
          resolveLogin = () => resolve({ success: true })
        })
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      const loginPromise = wrapper.vm.handleLogin()
      await flushPromises()

      expect(wrapper.find('button').text()).toBe('登录中...')

      resolveLogin()
      await loginPromise
      await flushPromises()

      expect(wrapper.find('button').text()).toBe('登录')
    })
  })

  describe('登录失败流程', () => {
    it('登录失败显示错误信息', async () => {
      wrapper = createWrapper()
      mockLogin.mockResolvedValue({ success: false, error: '用户名或密码错误' })

      wrapper.vm.form.username = 'wronguser'
      wrapper.vm.form.password = 'wrongpass'
      await wrapper.vm.handleLogin()
      await flushPromises()

      expect(wrapper.vm.error).toBe('用户名或密码错误')
    })

    it('登录失败不跳转路由', async () => {
      wrapper = createWrapper()
      mockLogin.mockResolvedValue({ success: false, error: '用户名或密码错误' })

      wrapper.vm.form.username = 'wronguser'
      wrapper.vm.form.password = 'wrongpass'
      await wrapper.vm.handleLogin()
      await flushPromises()

      expect(mockPush).not.toHaveBeenCalled()
    })

    it('登录失败后 loading 状态应为 false', async () => {
      wrapper = createWrapper()
      mockLogin.mockResolvedValue({ success: false, error: '用户名或密码错误' })

      wrapper.vm.form.username = 'wronguser'
      wrapper.vm.form.password = 'wrongpass'
      await wrapper.vm.handleLogin()
      await flushPromises()

      expect(wrapper.vm.loading).toBe(false)
    })

    it('登录失败后错误信息显示在页面上', async () => {
      wrapper = createWrapper()
      mockLogin.mockResolvedValue({ success: false, error: '用户名或密码错误' })

      wrapper.vm.form.username = 'wronguser'
      wrapper.vm.form.password = 'wrongpass'
      await wrapper.vm.handleLogin()
      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.find('.error-message').text()).toBe('用户名或密码错误')
    })
  })

})
