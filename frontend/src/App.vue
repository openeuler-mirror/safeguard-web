<template>
  <router-view />
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'App',
  mounted() {
    // 初始化时尝试恢复登录状态
    this.fetchUser()
  },
  methods: {
    ...mapActions('auth', ['fetchUser'])
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>