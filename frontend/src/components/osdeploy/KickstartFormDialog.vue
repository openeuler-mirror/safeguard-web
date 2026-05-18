<template>
  <div v-if="visible" class="dialog-overlay" @click.self="close">
    <div class="dialog dialog-wide">
      <div class="dialog-header">
        <h3>{{ isEdit ? '编辑模板' : '创建模板' }}</h3>
        <button class="dialog-close" @click="close">&times;</button>
      </div>
      <div class="dialog-body">
        <div v-if="formError" class="form-error-summary">{{ formError }}</div>
        <KickstartEditor ref="editor" :kickstart="kickstart" @update:formData="onFormDataChange" />
      </div>
      <div class="dialog-footer">
        <button class="btn-cancel" @click="close">取消</button>
        <button class="btn-primary" @click="submit">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import KickstartEditor from './KickstartEditor.vue'
import { createKickstart, updateKickstart } from '@/api/osdeploy/kickstart'

export default {
  name: 'KickstartFormDialog',
  components: {
    KickstartEditor
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    kickstart: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'success'],
  data() {
    return {
      isEdit: false,
      formError: '',
      formData: null
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
      this.isEdit = !!this.kickstart
      this.formError = ''
    },
    onFormDataChange(data) {
      this.formData = data
    },
    close() {
      this.$emit('close')
    },
    async submit() {
      if (!this.$refs.editor.validate()) {
        return
      }
      try {
        const data = this.$refs.editor.getData()
        if (this.isEdit) {
          await updateKickstart(this.kickstart.id, data)
        } else {
          await createKickstart(data)
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

.dialog-wide {
  width: 800px;
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

.form-error-summary {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  color: #f56c6c;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
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