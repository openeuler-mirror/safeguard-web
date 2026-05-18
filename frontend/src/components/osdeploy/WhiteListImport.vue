<template>
  <div v-if="visible" class="dialog-overlay" @click.self="close">
    <div class="dialog">
      <div class="dialog-header">
        <h3>批量导入白名单</h3>
        <button class="dialog-close" @click="close">&times;</button>
      </div>
      <div class="dialog-body">
        <div class="form-item">
          <label>选择文件</label>
          <input type="file" ref="fileInput" accept=".xlsx,.xls,.csv" @change="handleFileChange" />
          <span class="help-text">支持 .xlsx, .xls, .csv 格式</span>
        </div>
        <div v-if="uploadProgress > 0" class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <span>{{ uploadProgress }}%</span>
        </div>
        <div class="template-download">
          <a href="/static/templates/whitelist_import_template.xlsx" download>下载导入模板</a>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="btn-cancel" @click="close">取消</button>
        <button class="btn-primary" @click="handleImport" :disabled="!selectedFile || uploading">
          {{ uploading ? '导入中...' : '开始导入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { importWhiteList } from '@/api/osdeploy/whitelist'

export default {
  name: 'WhiteListImport',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'success'],
  data() {
    return {
      selectedFile: null,
      uploading: false,
      uploadProgress: 0
    }
  },
  watch: {
    visible(val) {
      if (!val) {
        this.reset()
      }
    }
  },
  methods: {
    reset() {
      this.selectedFile = null
      this.uploading = false
      this.uploadProgress = 0
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },
    handleFileChange(e) {
      const file = e.target.files[0]
      if (file) {
        this.selectedFile = file
      }
    },
    close() {
      this.$emit('close')
    },
    async handleImport() {
      if (!this.selectedFile) return

      this.uploading = true
      this.uploadProgress = 0
      try {
        this.uploadProgress = 50
        await importWhiteList(this.selectedFile)
        this.uploadProgress = 100
        this.$emit('success')
        this.close()
      } catch (e) {
        alert(e.message || '导入失败')
      } finally {
        this.uploading = false
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

.form-item input[type="file"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.help-text {
  display: block;
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.template-download {
  margin-top: 16px;
}

.template-download a {
  color: #409eff;
  text-decoration: none;
}

.template-download a:hover {
  text-decoration: underline;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e4e4e4;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  transition: width 0.3s;
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

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>