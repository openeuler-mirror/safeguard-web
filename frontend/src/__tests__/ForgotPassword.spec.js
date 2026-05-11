import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ForgotPassword from '@/views/ForgotPassword.vue'

// Mock API
vi.mock('@/api/auth', () => ({
  sendVerificationCode: vi.fn(),
  resetPasswordWithCode: vi.fn()
}))

import { sendVerificationCode, resetPasswordWithCode } from '@/api/auth'

const createWrapper = () => {
  return mount(ForgotPassword, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('ForgotPassword.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染邮箱输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('#email').exists()).toBe(true)
    })

    it('渲染验证码输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('#code').exists()).toBe(true)
    })

    it('渲染新密码输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('#newPassword').exists()).toBe(true)
    })

    it('渲染确认密码输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('#confirmPassword').exists()).toBe(true)
    })

    it('渲染发送验证码按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.send-code-btn').exists()).toBe(true)
    })

    it('渲染重置密码按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.submit-btn').exists()).toBe(true)
    })

    it('渲染返回登录链接', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.link-group a').exists()).toBe(true)
    })
  })

  describe('表单验证', () => {
    it('重置密码时提示请输入邮箱', async () => {
      const wrapper = createWrapper()
      await wrapper.find('.submit-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('请输入邮箱')
    })

    it('重置密码时提示请输入6位验证码', async () => {
      const wrapper = createWrapper()
      await wrapper.find('#email').setValue('test@example.com')
      await wrapper.find('.submit-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('请输入6位验证码')
    })

    it('密码少于6位时提示密码长度至少6位', async () => {
      const wrapper = createWrapper()
      await wrapper.find('#email').setValue('test@example.com')
      await wrapper.find('#code').setValue('123456')
      await wrapper.find('#newPassword').setValue('123')
      await wrapper.find('.submit-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('密码长度至少6位')
    })

    it('两次密码不一致时提示密码不一致', async () => {
      const wrapper = createWrapper()
      await wrapper.find('#email').setValue('test@example.com')
      await wrapper.find('#code').setValue('123456')
      await wrapper.find('#newPassword').setValue('123456')
      await wrapper.find('#confirmPassword').setValue('654321')
      await wrapper.find('.submit-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('两次输入的密码不一致')
    })
  })

  describe('发送验证码', () => {
    it('未输入邮箱时提示请输入邮箱且不调用API', async () => {
      const wrapper = createWrapper()
      await wrapper.find('.send-code-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('请输入邮箱')
      expect(sendVerificationCode).not.toHaveBeenCalled()
    })

    it('输入邮箱后点击发送验证码', async () => {
      const wrapper = createWrapper()
      sendVerificationCode.mockResolvedValue({ local_verify_url: null })
      await wrapper.find('#email').setValue('test@example.com')
      await wrapper.find('.send-code-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(sendVerificationCode).toHaveBeenCalledWith('test@example.com', 'forgot')
    })

    it('发送验证码成功后启动倒计时', async () => {
      const wrapper = createWrapper()
      sendVerificationCode.mockResolvedValue({ local_verify_url: null })
      await wrapper.find('#email').setValue('test@example.com')
      await wrapper.find('.send-code-btn').trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.countdown).toBe(60)
    })
  })

  describe('重置密码成功', () => {
    it('所有条件满足时调用 resetPasswordWithCode', async () => {
      const wrapper = createWrapper()
      resetPasswordWithCode.mockResolvedValue({ errmsg: 'success' })
      const routerPush = vi.fn()
      wrapper.vm.$router = { push: routerPush }

      await wrapper.find('#email').setValue('test@example.com')
      await wrapper.find('#code').setValue('123456')
      await wrapper.find('#newPassword').setValue('123456')
      await wrapper.find('#confirmPassword').setValue('123456')

      await wrapper.find('.submit-btn').trigger('click')
      await wrapper.vm.$nextTick()

      expect(resetPasswordWithCode).toHaveBeenCalledWith('test@example.com', '123456', '123456')
    })
  })

  describe('验证码输入框样式', () => {
    it('验证码输入框有 code-input class', () => {
      const wrapper = createWrapper()
      const codeInput = wrapper.find('#code')
      expect(codeInput.classes()).toContain('code-input')
    })
  })
})
