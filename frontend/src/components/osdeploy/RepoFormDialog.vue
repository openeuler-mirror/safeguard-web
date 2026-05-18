<template>
  <div v-if="visible" class="dialog-overlay" @click.self="close">
    <div class="dialog">
      <div class="dialog-header">
        <h3>{{ isEdit ? '编辑仓库' : '创建仓库' }}</h3>
        <button class="dialog-close" @click="close">&times;</button>
      </div>
      <div class="dialog-body">
        <div v-if="formError" class="form-error-summary">{{ formError }}</div>
        <div class="form-item">
          <label>仓库名称 <span class="required">*</span></label>
          <input v-model="form.name" type="text" placeholder="请输入仓库名称" :class="{ 'input-error': errors.name }" />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
        </div>
        <div class="form-item">
          <label>仓库类型 <span class="required">*</span></label>
          <select v-model="form.repo_type" :class="{ 'input-error': errors.repo_type }">
            <option value="yum">YUM</option>
            <option value="iso">ISO</option>
            <option value="http">HTTP</option>
          </select>
          <span v-if="errors.repo_type" class="field-error">{{ errors.repo_type }}</span>
        </div>
        <div class="form-item">
          <label>仓库地址 <span class="required">*</span></label>
          <input v-model="form.base_url" type="text" placeholder="如: http://mirror.example.com/centos" :class="{ 'input-error': errors.base_url }" />
          <span v-if="errors.base_url" class="field-error">{{ errors.base_url }}</span>
        </div>
        <div class="form-item">
          <label>描述</label>
          <textarea v-model="form.description" placeholder="请输入描述信息" rows="3"></textarea>
        </div>
        <div class="form-item">
          <label>
            <input v-model="form.is_default" type="checkbox" />
            设为默认仓库
          </label>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="btn-cancel" @click="close">取消</button>
        <button class="btn-primary" @click="submit">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import { createRepo, updateRepo } from '@/api/osdeploy/repo'

export default {
  name: 'RepoFormDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    repo: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'success'],
  data() {
    return {
      isEdit: false,
      formError: '',
      errors: {},
      form: {
        name: '',
        repo_type: 'yum',
        base_url: '',
        description: '',
        is_default: false
      }
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.initForm()
      }
    }
  },
  methods: {
    initForm() {
      this.isEdit = !!this.repo
      this.formError = ''
      this.errors = {}
      if (this.repo) {
        this.form = {
          name: this.repo.name,
          repo_type: this.repo.repo_type,
          base_url: this.repo.base_url,
          description: this.repo.description || '',
          is_default: this.repo.is_default
        }
      } else {
        this.form = {
          name: '',
          repo_type: 'yum',
          base_url: '',
          description: '',
          is_default: false
        }
      }
    },
    close() {
      this.$emit('close')
    },
    async submit() {
      this.formError = ''
      this.errors = {}

      if (!this.form.name.trim()) {
        this.errors.name = '请输入仓库名称'
        return
      }
      if (!this.form.base_url.trim()) {
        this.errors.base_url = '请输入仓库地址'
        return
      }

      try {
        if (this.isEdit) {
          await updateRepo(this.repo.id, this.form)
        } else {
          await createRepo(this.form)
        }
        this.$emit('success')
        this.close()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    }
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.dialog-close:hover {
  color: #666;
}

.dialog-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.form-item {
  margin-bottom: 16px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
}

.form-item input[type="text"],
.form-item select,
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-item textarea {
  resize: vertical;
}

.required {
  color: #f56c6c;
}

.form-error-summary {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  color: #f56c6c;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
}

.input-error {
  border-color: #f56c6c !important;
}

.field-error {
  display: block;
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

.btn-cancel {
  padding: 8px 16px;
  background: #fff;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-primary {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background: #66b1ff;
}
</style>