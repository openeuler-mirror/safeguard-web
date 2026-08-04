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

})
