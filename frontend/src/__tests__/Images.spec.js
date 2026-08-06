import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Images from '@/views/Images.vue'
import { getImages, createImage, updateImage, deleteImage, refreshImages, getHosts } from '@/api/host'

vi.mock('@/api/host')

describe('Images 页面测试', () => {
  let wrapper

  const mockImages = [
    { id: 1, name: 'CentOS-7', ostype: 'centos', path: '/var/lib/libvirt/images/centos7.qcow2', host: 1, host_name: 'host-1', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'Ubuntu-20.04', ostype: 'ubuntu', path: '/var/lib/libvirt/images/ubuntu20.qcow2', host: 2, host_name: 'host-2', created_at: '2024-01-02T00:00:00Z' }
  ]

  const mockHostList = [
    { id: 1, hostname: 'host-1', ip_address: '192.168.1.100' },
    { id: 2, hostname: 'host-2', ip_address: '192.168.1.101' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getImages.mockResolvedValue({ results: mockImages })
    getHosts.mockResolvedValue({ results: mockHostList })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
    vi.spyOn(console, 'error').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Images, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getImages 和 getHosts', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getImages).toHaveBeenCalled()
      expect(getHosts).toHaveBeenCalled()
    })

    it('应该显示镜像列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('CentOS-7')
      expect(wrapper.text()).toContain('Ubuntu-20.04')
      expect(wrapper.text()).toContain('host-1')
      expect(wrapper.text()).toContain('host-2')
    })

    it('应该显示操作系统类型', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('CentOS')
      expect(wrapper.text()).toContain('Ubuntu')
    })

    it('应该显示加载状态', async () => {
      getImages.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

  describe('创建镜像', () => {
    it('点击添加镜像按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('创建成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createImage.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.id = 'img-001'
      wrapper.vm.form.name = 'Test-Image'
      wrapper.vm.form.host = 1
      wrapper.vm.form.path = '/path/to/image.qcow2'
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createImage).toHaveBeenCalled()
      expect(getImages).toHaveBeenCalledTimes(2)
    })

    it('表单验证应该正常工作', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.id = ''
      wrapper.vm.form.name = ''
      wrapper.vm.form.host = null
      wrapper.vm.form.path = ''
      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.id).toBe('请输入镜像ID')
      expect(wrapper.vm.errors.name).toBe('请输入镜像名称')
      expect(wrapper.vm.errors.host).toBe('请选择宿主机')
      expect(wrapper.vm.errors.path).toBe('请输入镜像路径')
      expect(createImage).not.toHaveBeenCalled()
    })

    it('创建失败时应该显示错误信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createImage.mockRejectedValue(new Error('创建失败'))

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.id = 'img-001'
      wrapper.vm.form.name = 'Test-Image'
      wrapper.vm.form.host = 1
      wrapper.vm.form.path = '/path/to/image.qcow2'
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(wrapper.vm.formError).toBe('创建失败')
    })
  })

  describe('编辑镜像', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.name).toBe('CentOS-7')
    })

    it('编辑成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateImage.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateImage).toHaveBeenCalled()
      expect(getImages).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除镜像', () => {
    it('点击删除按钮应该打开确认弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-delete')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
    })

    it('确认删除后应该调用 API 并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteImage.mockResolvedValue({})

      await wrapper.findAll('button.btn-delete')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteImage).toHaveBeenCalledWith(1)
      expect(getImages).toHaveBeenCalledTimes(2)
    })

    it('删除失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteImage.mockRejectedValue(new Error('删除失败'))

      await wrapper.findAll('button.btn-delete')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('删除失败')
    })
  })

  describe('刷新镜像', () => {
    it('点击刷新按钮应该调用 refreshImages 并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      refreshImages.mockResolvedValue({})

      await wrapper.findAll('button.btn-refresh')[0].trigger('click')
      await flushPromises()

      expect(refreshImages).toHaveBeenCalledWith(1)
      expect(getImages).toHaveBeenCalledTimes(2)
    })

    it('刷新失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      refreshImages.mockRejectedValue(new Error('刷新失败'))

      await wrapper.findAll('button.btn-refresh')[0].trigger('click')
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('刷新失败')
    })
  })

  describe('搜索和过滤', () => {
    it('按回车搜索应该调用 loadImages', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.searchName = 'centos'
      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('centos')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getImages).toHaveBeenCalledWith(expect.objectContaining({ search: 'centos' }))
    })

    it('改变过滤条件应该调用 loadImages', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterHost = '1'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getImages).toHaveBeenCalledWith(expect.objectContaining({ host: '1' }))
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getImages.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

})
