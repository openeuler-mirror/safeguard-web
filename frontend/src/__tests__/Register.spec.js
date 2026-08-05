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

  describe('发送验证码功能', () => {
    it('未输入邮箱时点击发送验证码显示错误', async () => {
      wrapper = createWrapper()

      await wrapper.find('.send-code-btn').trigger('click')

      expect(wrapper.vm.error).toBe('请先输入邮箱')
    })

    it('输入邮箱后点击发送验证码调用 API', async () => {
      wrapper = createWrapper()
      sendVerificationCode.mockResolvedValue({})

      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleSendCode()

      expect(sendVerificationCode).toHaveBeenCalledWith('test@example.com', 'register')
    })

    it('发送验证码成功后启动 60 秒倒计时', async () => {
      wrapper = createWrapper()
      sendVerificationCode.mockResolvedValue({})

      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleSendCode()
      await flushPromises()

      expect(wrapper.vm.countdown).toBe(60)
    })

    it('倒计时过程中按钮显示倒计时', async () => {
      wrapper = createWrapper()
      sendVerificationCode.mockResolvedValue({})

      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleSendCode()
      await flushPromises()

      expect(wrapper.find('.send-code-btn').text()).toBe('60s')
    })

    it('发送验证码返回本地验证URL时设置 localVerifyUrl', async () => {
      wrapper = createWrapper()
      sendVerificationCode.mockResolvedValue({ local_verify_url: 'http://test-verify.com' })

      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleSendCode()
      await flushPromises()

      expect(wrapper.vm.localVerifyUrl).toBe('http://test-verify.com')
    })

    it('localVerifyUrl 存在时显示验证码输入框', async () => {
      wrapper = createWrapper()
      wrapper.vm.localVerifyUrl = 'http://test-verify.com'
      await flushPromises()

      expect(wrapper.find('#code').exists()).toBe(true)
    })

    it('发送验证码失败显示错误信息', async () => {
      wrapper = createWrapper()
      sendVerificationCode.mockRejectedValue(new Error('发送验证码失败'))

      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleSendCode()
      await flushPromises()

      expect(wrapper.vm.error).toBe('发送验证码失败')
    })

    it('发送验证码过程中 codeSending 为 true', async () => {
      wrapper = createWrapper()
      let resolveSendCode
      sendVerificationCode.mockImplementation(() => {
        return new Promise(resolve => {
          resolveSendCode = () => resolve({})
        })
      })

      wrapper.vm.form.email = 'test@example.com'
      const sendCodePromise = wrapper.vm.handleSendCode()

      expect(wrapper.vm.codeSending).toBe(true)

      resolveSendCode()
      await sendCodePromise
      await flushPromises()

      expect(wrapper.vm.codeSending).toBe(false)
    })
  })

  describe('注册功能', () => {
    it('两次密码不一致时显示错误', async () => {
      wrapper = createWrapper()

      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password456'
      await wrapper.vm.handleRegister()

      expect(wrapper.vm.error).toBe('两次输入的密码不一致')
      expect(createUser).not.toHaveBeenCalled()
    })

    it('两次密码一致时调用 createUser API', async () => {
      wrapper = createWrapper()
      createUser.mockResolvedValue({})

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(createUser).toHaveBeenCalledWith(wrapper.vm.form)
    })

    it('本地验证模式且有验证码时先调用 verifyCode', async () => {
      wrapper = createWrapper()
      verifyCode.mockResolvedValue({})
      createUser.mockResolvedValue({})

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      wrapper.vm.localVerifyUrl = 'test-url'
      wrapper.vm.verificationCode = '123456'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(verifyCode).toHaveBeenCalledWith('test@example.com', '123456')
      expect(createUser).toHaveBeenCalled()
    })

    it('邮箱验证失败时不调用 createUser', async () => {
      wrapper = createWrapper()
      verifyCode.mockRejectedValue(new Error('验证失败'))

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      wrapper.vm.localVerifyUrl = 'test-url'
      wrapper.vm.verificationCode = 'wrong-code'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(wrapper.vm.error).toBe('邮箱验证失败，请先完成验证')
      expect(createUser).not.toHaveBeenCalled()
    })

    it('注册成功后设置 success 为 true', async () => {
      wrapper = createWrapper()
      createUser.mockResolvedValue({})

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(wrapper.vm.success).toBe(true)
    })

    it('注册成功后显示成功消息', async () => {
      wrapper = createWrapper()
      createUser.mockResolvedValue({})

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(wrapper.find('.success-message').exists()).toBe(true)
      expect(wrapper.find('.success-message').text()).toBe('注册成功！正在跳转...')
    })

    it('注册成功后 1.5 秒跳转到登录页面', async () => {
      wrapper = createWrapper()
      createUser.mockResolvedValue({})

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(mockPush).not.toHaveBeenCalled()

      vi.advanceTimersByTime(1500)
      await flushPromises()

      expect(mockPush).toHaveBeenCalledWith('/login')
    })

    it('注册失败显示错误信息', async () => {
      wrapper = createWrapper()
      createUser.mockRejectedValue(new Error('用户名已存在'))

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      await wrapper.vm.handleRegister()
      await flushPromises()

      expect(wrapper.vm.error).toBe('用户名已存在')
      expect(wrapper.vm.success).toBe(false)
    })

    it('注册过程中 loading 为 true', async () => {
      wrapper = createWrapper()
      let resolveRegister
      createUser.mockImplementation(() => {
        return new Promise(resolve => {
          resolveRegister = () => resolve({})
        })
      })

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      const registerPromise = wrapper.vm.handleRegister()

      expect(wrapper.vm.loading).toBe(true)

      resolveRegister()
      await registerPromise
      await flushPromises()

      expect(wrapper.vm.loading).toBe(false)
    })

    it('注册过程中按钮显示"注册中..."', async () => {
      wrapper = createWrapper()
      createUser.mockResolvedValue({})

      wrapper.vm.form.user = 'testuser'
      wrapper.vm.form.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      wrapper.vm.form.email = 'test@example.com'
      wrapper.vm.loading = true
      await flushPromises()

      expect(wrapper.find('button[type="submit"]').text()).toBe('注册中...')
    })
  })

  describe('输入框属性验证', () => {
    it('密码输入框有 minlength="6" 属性', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#password').attributes('minlength')).toBe('6')
    })

    it('邮箱输入框类型是 email', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#email').attributes('type')).toBe('email')
    })
  })

  describe('渲染链接', () => {
    it('应有去登录的链接', async () => {
      wrapper = createWrapper()
      // 检查有链接区域
      expect(wrapper.find('.link-group').exists()).toBe(true)
    })
  })
})
