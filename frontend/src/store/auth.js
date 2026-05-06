import { login, logout, getMe } from '@/api/auth'
import api from '@/api/auth'

export default {
  namespaced: true,

  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    menus: [],
  }),

  mutations: {
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    CLEAR_AUTH(state) {
      state.user = null
      state.isAuthenticated = false
      state.menus = []
    },
    SET_MENUS(state, menus) {
      state.menus = menus
    },
  },

  actions: {
    async login({ commit }, { username, password }) {
      commit('SET_LOADING', true)
      try {
        const res = await login(username, password)
        const { access, refresh } = res.data
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)

        // 获取用户信息
        const userRes = await getMe()
        commit('SET_USER', userRes.data)

        // 获取用户菜单
        await this.dispatch('auth/fetchMenus')

        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '登录失败' }
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async logout({ commit }) {
      logout()
      commit('CLEAR_AUTH')
    },

    async fetchUser({ commit }) {
      const token = localStorage.getItem('access_token')
      if (!token) {
        commit('CLEAR_AUTH')
        return
      }
      try {
        const res = await getMe()
        commit('SET_USER', res.data)
      } catch (error) {
        commit('CLEAR_AUTH')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    },

    async fetchMenus({ commit }) {
      try {
        const res = await api.get('/users/me/menus/')
        commit('SET_MENUS', res.data)
      } catch (error) {
        console.error('获取菜单失败', error)
      }
    },
  },

  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    user: (state) => state.user,
    menus: (state) => state.menus,
  },
}