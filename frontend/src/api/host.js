import api from './auth'

// ========== Cluster ==========

// 获取集群列表
export function getClusters(params) {
  return api.get('/clusters/', { params })
}

// 获取集群详情
export function getCluster(id) {
  return api.get(`/clusters/${id}/`)
}

// 创建集群
export function createCluster(data) {
  return api.post('/clusters/', data)
}

// 更新集群
export function updateCluster(id, data) {
  return api.put(`/clusters/${id}/`, data)
}

// 删除集群
export function deleteCluster(id) {
  return api.delete(`/clusters/${id}/`)
}

// 获取集群树下拉（用于下拉选择）
export function getClusterTree() {
  return api.get('/clusters/tree/')
}

// 获取集群拓扑
export function getClusterTopology(id) {
  return api.get(`/clusters/${id}/topology/`)
}

// 获取集群关联的主机列表
export function getClusterHosts(id) {
  return api.get(`/clusters/${id}/hosts/`)
}

// ========== Host ==========

// 获取主机列表
export function getHosts(params) {
  return api.get('/hosts/', { params })
}

// 获取主机详情
export function getHost(id) {
  return api.get(`/hosts/${id}/`)
}

// 创建主机
export function createHost(data) {
  return api.post('/hosts/', data)
}

// 更新主机
export function updateHost(id, data) {
  return api.put(`/hosts/${id}/`, data)
}

// 删除主机
export function deleteHost(id) {
  return api.delete(`/hosts/${id}/`)
}

// 采集主机硬件信息
export function collectHardware(id) {
  return api.post(`/hosts/${id}/collect_hardware/`)
}

// 采集主机 LLDP 信息
export function collectLLDP(id) {
  return api.post(`/hosts/${id}/collect_lldp/`)
}

// 采集主机全部信息
export function collectAll(id) {
  return api.post(`/hosts/${id}/collect_all/`)
}

// 修改主机密码
export function updateHostPassword(id, data) {
  return api.post(`/hosts/${id}/update_password/`, data)
}

// ========== VM ==========

// 获取VM列表
export function getVMs(params) {
  return api.get('/vms/', { params })
}

// 获取VM详情
export function getVM(id) {
  return api.get(`/vms/${id}/`)
}

// 创建VM
export function createVM(data) {
  return api.post('/vms/', data)
}

// 更新VM
export function updateVM(id, data) {
  return api.put(`/vms/${id}/`, data)
}

// 删除VM
export function deleteVM(id) {
  return api.delete(`/vms/${id}/`)
}

// 启动VM
export function startVM(id) {
  return api.post(`/vms/${id}/start/`)
}

// 停止VM
export function stopVM(id) {
  return api.post(`/vms/${id}/stop/`)
}

// 重启VM
export function rebootVM(id) {
  return api.post(`/vms/${id}/reboot/`)
}

// 暂停VM
export function pauseVM(id) {
  return api.post(`/vms/${id}/pause/`)
}

// 恢复VM
export function resumeVM(id) {
  return api.post(`/vms/${id}/resume/`)
}

// 获取VM状态
export function getVMStatus(id) {
  return api.get(`/vms/${id}/status/`)
}

// ========== Image ==========

// 获取镜像列表
export function getImages(params) {
  return api.get('/images/', { params })
}

// 获取镜像详情
export function getImage(id) {
  return api.get(`/images/${id}/`)
}

// 创建镜像
export function createImage(data) {
  return api.post('/images/', data)
}

// 更新镜像
export function updateImage(id, data) {
  return api.put(`/images/${id}/`, data)
}

// 删除镜像
export function deleteImage(id) {
  return api.delete(`/images/${id}/`)
}

// 根据主机获取镜像列表
export function getImagesByHost(hostId) {
  return api.get('/images/list_by_host/', { params: { host_id: hostId } })
}

// 刷新镜像列表
export function refreshImages(id) {
  return api.post(`/images/${id}/refresh/`)
}