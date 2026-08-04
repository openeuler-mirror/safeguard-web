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

  describe('页面初始状态', () => {
    it('应渲染注册表单', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.register-container').exists()).toBe(true)
      expect(wrapper.find('.register-box').exists()).toBe(true)
    })

    it('应显示"用户注册"标题', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('用户注册')
    })

    it('应有用户名输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#username').exists()).toBe(true)
    })

    it('应有密码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#password').exists()).toBe(true)
    })

    it('应有确认密码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#confirmPassword').exists()).toBe(true)
    })

    it('应有昵称输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#nickname').exists()).toBe(true)
    })

    it('应有手机号输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#phone').exists()).toBe(true)
    })

    it('应有邮箱输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#email').exists()).toBe(true)
    })

    it('应有发送验证码按钮', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.send-code-btn').exists()).toBe(true)
      expect(wrapper.find('.send-code-btn').text()).toBe('发送验证码')
    })

    it('应有注册按钮', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').text()).toBe('注册')
    })

    it('初始 loading 状态应为 false', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(false)
    })

    it('初始 error 状态应为空', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.error).toBe('')
    })

    it('初始 success 状态应为 false', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.success).toBe(false)
    })

    it('初始 countdown 状态应为 0', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.countdown).toBe(0)
    })

    it('初始 localVerifyUrl 状态应为空', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.localVerifyUrl).toBe('')
    })

    it('初始不显示验证码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#code').exists()).toBe(false)
    })
  })

  describe('表单数据绑定', () => {
    it('v-model 正确绑定用户名', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#username')

      await input.setValue('testuser')

      expect(wrapper.vm.form.user).toBe('testuser')
    })

    it('v-model 正确绑定密码', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#password')

      await input.setValue('password123')

      expect(wrapper.vm.form.password).toBe('password123')
    })

    it('v-model 正确绑定确认密码', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#confirmPassword')

      await input.setValue('password123')

      expect(wrapper.vm.confirmPassword).toBe('password123')
    })

    it('v-model 正确绑定昵称', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#nickname')

      await input.setValue('Test User')

      expect(wrapper.vm.form.nickname).toBe('Test User')
    })

    it('v-model 正确绑定手机号', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#phone')

      await input.setValue('13800138000')

      expect(wrapper.vm.form.phone).toBe('13800138000')
    })

    it('v-model 正确绑定邮箱', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#email')

      await input.setValue('test@example.com')

      expect(wrapper.vm.form.email).toBe('test@example.com')
    })

    it('v-model 正确绑定验证码', async () => {
      wrapper = createWrapper()
      wrapper.vm.localVerifyUrl = 'test-url'
      await flushPromises()

      const input = wrapper.find('#code')
      await input.setValue('123456')

      expect(wrapper.vm.verificationCode).toBe('123456')
    })
  })

})
