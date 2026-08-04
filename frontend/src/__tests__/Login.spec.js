import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Login from '@/views/Login.vue'

const createWrapper = () => {
  return mount(Login, {
    global: {
      stubs: {
        'router-link': true
      },
      mocks: {
        $store: {
          dispatch: vi.fn()
        },
        $router: {
          push: vi.fn()
        }
      }
    }
  })
}

describe('Login 页面测试', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

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

  describe('登录按钮状态', () => {
    it('loading 时按钮被禁用', async () => {
      wrapper = createWrapper()
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    })

    it('非 loading 时按钮可用', async () => {
      wrapper = createWrapper()
      wrapper.vm.loading = false
      await wrapper.vm.$nextTick()

      expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
    })
  })

  describe('输入框属性', () => {
    it('用户名输入框类型是 text', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#username').attributes('type')).toBe('text')
    })

    it('密码输入框类型是 password', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#password').attributes('type')).toBe('password')
    })

    it('用户名输入框有 required 属性', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#username').attributes('required')).toBeDefined()
    })

    it('密码输入框有 required 属性', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#password').attributes('required')).toBeDefined()
    })
  })
})
