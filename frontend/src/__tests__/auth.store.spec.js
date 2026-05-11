import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createStore } from 'vuex'
import auth from '@/store/auth'

// Mock API
vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  getMe: vi.fn()
}))

import { login, logout, getMe } from '@/api/auth'

describe('auth store', () => {
  let store

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    store = createStore({
      ...auth
    })
  })

  describe('state', () => {
    it('初始状态 user 为 null', () => {
      expect(store.state.user).toBe(null)
    })

    it('初始状态 isAuthenticated 为 false', () => {
      expect(store.state.isAuthenticated).toBe(false)
    })

    it('初始状态 menus 为空数组', () => {
      expect(store.state.menus).toEqual([])
    })
  })

  describe('mutations', () => {
    it('SET_USER 设置用户并更新 isAuthenticated', () => {
      const user = { id: 1, username: 'test' }
      store.commit('SET_USER', user)
      expect(store.state.user).toEqual(user)
      expect(store.state.isAuthenticated).toBe(true)
    })

    it('CLEAR_AUTH 清除用户状态', () => {
      store.commit('SET_USER', { id: 1, username: 'test' })
      store.commit('CLEAR_AUTH')
      expect(store.state.user).toBe(null)
      expect(store.state.isAuthenticated).toBe(false)
      expect(store.state.menus).toEqual([])
    })

    it('SET_LOADING 设置加载状态', () => {
      store.commit('SET_LOADING', true)
      expect(store.state.loading).toBe(true)
    })

    it('SET_MENUS 设置菜单', () => {
      const menus = [{ path: '/dashboard', name: 'Dashboard' }]
      store.commit('SET_MENUS', menus)
      expect(store.state.menus).toEqual(menus)
    })
  })

  describe('actions', () => {
    describe('login', () => {
      it('登录成功时设置用户和token', async () => {
        const mockUser = { id: 1, username: 'test' }
        login.mockResolvedValue({ access: 'access-token', refresh: 'refresh-token' })
        getMe.mockResolvedValue(mockUser)

        const result = await store.dispatch('login', { username: 'test', password: '123456' })

        expect(result.success).toBe(true)
        expect(localStorage.getItem('access_token')).toBe('access-token')
        expect(localStorage.getItem('refresh_token')).toBe('refresh-token')
        expect(store.state.user).toEqual(mockUser)
      })

      it('登录失败时返回错误', async () => {
        const error = new Error('Invalid credentials')
        error.errno = 2001
        login.mockRejectedValue(error)

        const result = await store.dispatch('login', { username: 'test', password: 'wrong' })

        expect(result.success).toBe(false)
        expect(result.error).toBe('Invalid credentials')
      })
    })

    describe('logout', () => {
      it('登出时调用 logout 函数并清除状态', () => {
        store.commit('SET_USER', { id: 1 })
        store.commit('SET_MENUS', [{ path: '/test' }])

        store.dispatch('logout')

        expect(logout).toHaveBeenCalled()
        expect(store.state.user).toBeNull()
        expect(store.state.menus).toEqual([])
      })
    })

    describe('fetchUser', () => {
      it('无token时清除用户状态', async () => {
        store.commit('SET_USER', { id: 1 })
        await store.dispatch('fetchUser')
        expect(store.state.user).toBeNull()
      })

      it('有token时获取用户信息', async () => {
        const mockUser = { id: 1, username: 'test' }
        localStorage.setItem('access_token', 'valid-token')
        getMe.mockResolvedValue(mockUser)

        await store.dispatch('fetchUser')

        expect(store.state.user).toEqual(mockUser)
      })

      it('获取用户信息失败时清除状态和token', async () => {
        localStorage.setItem('access_token', 'invalid-token')
        getMe.mockRejectedValue(new Error('Unauthorized'))

        await store.dispatch('fetchUser')

        expect(store.state.user).toBeNull()
        expect(localStorage.getItem('access_token')).toBeNull()
      })
    })
  })

  describe('getters', () => {
    it('isAuthenticated 返回 isAuthenticated 状态', () => {
      store.commit('SET_USER', { id: 1 })
      expect(store.getters.isAuthenticated).toBe(true)

      store.commit('CLEAR_AUTH')
      expect(store.getters.isAuthenticated).toBe(false)
    })

    it('user 返回当前用户', () => {
      const user = { id: 1, username: 'test' }
      store.commit('SET_USER', user)
      expect(store.getters.user).toEqual(user)
    })

    it('menus 返回当前菜单', () => {
      const menus = [{ path: '/test' }]
      store.commit('SET_MENUS', menus)
      expect(store.getters.menus).toEqual(menus)
    })
  })
})
