import api from '../auth'

// 获取系统信息
export function getSystemInfo(hostId) {
  return api.get('/safeguard/host-info/system-info/', { params: { host_id: hostId } })
}

// 获取端口信息
export function getPortsInfo(hostId) {
  return api.get('/safeguard/host-info/ports-info/', { params: { host_id: hostId } })
}

// 获取进程信息
export function getProcessesInfo(hostId) {
  return api.get('/safeguard/host-info/processes-info/', { params: { host_id: hostId } })
}

// 获取服务信息
export function getServicesInfo(hostId) {
  return api.get('/safeguard/host-info/services-info/', { params: { host_id: hostId } })
}

// 获取系统账户信息
export function getAccountsInfo(hostId) {
  return api.get('/safeguard/host-info/accounts-info/', { params: { host_id: hostId } })
}

// 服务控制
export function controlService(hostId, data) {
  return api.post('/safeguard/host-info/service-control/', { host_id: hostId, ...data })
}

// 获取服务日志
export function getServiceLogs(hostId, serviceName, lines = 100) {
  return api.get('/safeguard/host-info/service-logs/', { params: { host_id: hostId, service_name: serviceName, lines } })
}

// 终止进程
export function killProcess(hostId, pid, force = false) {
  return api.post('/safeguard/host-info/kill-process/', { host_id: hostId, pid, force })
}

// 获取系统日志
export function getSystemLogs(hostId, params) {
  return api.get('/safeguard/host-info/system-logs/', { params: { host_id: hostId, ...params } })
}
