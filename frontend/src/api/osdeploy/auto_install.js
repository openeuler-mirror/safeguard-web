import api from './auth'

export function autoInstall(data) {
  return api.post('/autoinstall/auto_install/', data)
}

export function singleInstall(data) {
  return api.post('/autoinstall/single_install/', data)
}

export function batchInstall(data) {
  return api.post('/autoinstall/batch_install/', data)
}

export default {
  autoInstall,
  singleInstall,
  batchInstall,
}
