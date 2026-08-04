import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ChangePassword from '@/views/ChangePassword.vue'
import { changePassword } from '@/api/auth'

// 模拟 API 模块
vi.mock('@/api/auth')

describe('ChangePassword 页面测试', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(ChangePassword, {
      global: {
        mocks: {}
      }
    })
  }

  describe('页面初始状态', () => {
    it('应渲染修改密码表单', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.change-password-container').exists()).toBe(true)
      expect(wrapper.find('.change-password-box').exists()).toBe(true)
    })

    it('应显示"修改密码"标题', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('修改密码')
    })

    it('应有旧密码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#oldPassword').exists()).toBe(true)
    })

    it('应有新密码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#newPassword').exists()).toBe(true)
    })

    it('应有确认新密码输入框', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#confirmPassword').exists()).toBe(true)
    })

    it('应有确认修改按钮', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').text()).toBe('确认修改')
    })

    it('初始 loading 状态应为 false', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(false)
    })

    it('初始 error 状态应为空', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.error).toBe('')
    })

    it('初始 success 状态应为空', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.success).toBe('')
    })
  })

  describe('表单数据绑定', () => {
    it('v-model 正确绑定旧密码', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#oldPassword')

      await input.setValue('oldpassword')

      expect(wrapper.vm.form.old_password).toBe('oldpassword')
    })

    it('v-model 正确绑定新密码', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#newPassword')

      await input.setValue('newpassword123')

      expect(wrapper.vm.form.new_password).toBe('newpassword123')
    })

    it('v-model 正确绑定确认密码', async () => {
      wrapper = createWrapper()
      const input = wrapper.find('#confirmPassword')

      await input.setValue('newpassword123')

      expect(wrapper.vm.confirmPassword).toBe('newpassword123')
    })
  })

  describe('修改密码功能', () => {
    it('两次新密码不一致时显示错误', async () => {
      wrapper = createWrapper()

      wrapper.vm.form.old_password = 'oldpassword'
      wrapper.vm.form.new_password = 'password123'
      wrapper.vm.confirmPassword = 'password456'
      await wrapper.vm.handleChangePassword()

      expect(wrapper.vm.error).toBe('两次输入的新密码不一致')
      expect(changePassword).not.toHaveBeenCalled()
    })

    it('两次密码一致时调用 changePassword API', async () => {
      wrapper = createWrapper()
      changePassword.mockResolvedValue({})

      wrapper.vm.form.old_password = 'oldpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.handleChangePassword()
      await flushPromises()

      expect(changePassword).toHaveBeenCalledWith('oldpassword', 'newpassword123')
    })

    it('修改密码成功后显示成功消息', async () => {
      wrapper = createWrapper()
      changePassword.mockResolvedValue({})

      wrapper.vm.form.old_password = 'oldpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.handleChangePassword()
      await flushPromises()

      expect(wrapper.vm.success).toBe('密码修改成功')
      expect(wrapper.find('.success-message').exists()).toBe(true)
      expect(wrapper.find('.success-message').text()).toBe('密码修改成功')
    })

    it('修改密码成功后清空表单', async () => {
      wrapper = createWrapper()
      changePassword.mockResolvedValue({})

      wrapper.vm.form.old_password = 'oldpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.handleChangePassword()
      await flushPromises()

      expect(wrapper.vm.form.old_password).toBe('')
      expect(wrapper.vm.form.new_password).toBe('')
      expect(wrapper.vm.confirmPassword).toBe('')
    })

    it('修改密码失败显示错误信息', async () => {
      wrapper = createWrapper()
      changePassword.mockRejectedValue(new Error('旧密码错误'))

      wrapper.vm.form.old_password = 'wrongpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.handleChangePassword()
      await flushPromises()

      expect(wrapper.vm.error).toBe('旧密码错误')
      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.find('.error-message').text()).toBe('旧密码错误')
    })

    it('修改密码过程中 loading 为 true', async () => {
      wrapper = createWrapper()
      let resolveChangePassword
      changePassword.mockImplementation(() => {
        return new Promise(resolve => {
          resolveChangePassword = () => resolve({})
        })
      })

      wrapper.vm.form.old_password = 'oldpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      const changePasswordPromise = wrapper.vm.handleChangePassword()

      expect(wrapper.vm.loading).toBe(true)

      resolveChangePassword()
      await changePasswordPromise
      await flushPromises()

      expect(wrapper.vm.loading).toBe(false)
    })

    it('修改密码过程中按钮显示"修改中..."', async () => {
      wrapper = createWrapper()
      changePassword.mockResolvedValue({})

      wrapper.vm.loading = true
      await flushPromises()

      expect(wrapper.find('button[type="submit"]').text()).toBe('修改中...')
    })

    it('修改密码成功后清空错误信息', async () => {
      wrapper = createWrapper()
      changePassword.mockResolvedValue({})

      wrapper.vm.error = '之前的错误'
      wrapper.vm.form.old_password = 'oldpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.handleChangePassword()
      await flushPromises()

      expect(wrapper.vm.error).toBe('')
    })

    it('修改密码失败后清空成功信息', async () => {
      wrapper = createWrapper()
      changePassword.mockRejectedValue(new Error('旧密码错误'))

      wrapper.vm.success = '之前的成功'
      wrapper.vm.form.old_password = 'wrongpassword'
      wrapper.vm.form.new_password = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.handleChangePassword()
      await flushPromises()

      expect(wrapper.vm.success).toBe('')
    })
  })

  describe('输入框属性验证', () => {
    it('旧密码输入框类型是 password', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#oldPassword').attributes('type')).toBe('password')
    })

    it('新密码输入框类型是 password', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#newPassword').attributes('type')).toBe('password')
    })

    it('确认密码输入框类型是 password', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#confirmPassword').attributes('type')).toBe('password')
    })

    it('新密码输入框有 minlength="6" 属性', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#newPassword').attributes('minlength')).toBe('6')
    })

    it('所有输入框都有 required 属性', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('#oldPassword').attributes('required')).toBeDefined()
      expect(wrapper.find('#newPassword').attributes('required')).toBeDefined()
      expect(wrapper.find('#confirmPassword').attributes('required')).toBeDefined()
    })
  })

  describe('按钮状态', () => {
    it('loading 时按钮被禁用', async () => {
      wrapper = createWrapper()
      wrapper.vm.loading = true
      await flushPromises()

      expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    })

    it('非 loading 时按钮可用', async () => {
      wrapper = createWrapper()
      wrapper.vm.loading = false
      await flushPromises()

      expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
    })
  })

  describe('消息显示', () => {
    it('有 error 时显示错误消息', async () => {
      wrapper = createWrapper()
      wrapper.vm.error = '测试错误'
      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.find('.error-message').text()).toBe('测试错误')
    })

    it('有 success 时显示成功消息', async () => {
      wrapper = createWrapper()
      wrapper.vm.success = '测试成功'
      await flushPromises()

      expect(wrapper.find('.success-message').exists()).toBe(true)
      expect(wrapper.find('.success-message').text()).toBe('测试成功')
    })

    it('没有 error 时不显示错误消息', async () => {
      wrapper = createWrapper()
      wrapper.vm.error = ''
      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(false)
    })

    it('没有 success 时不显示成功消息', async () => {
      wrapper = createWrapper()
      wrapper.vm.success = ''
      await flushPromises()

      expect(wrapper.find('.success-message').exists()).toBe(false)
    })
  })
})
