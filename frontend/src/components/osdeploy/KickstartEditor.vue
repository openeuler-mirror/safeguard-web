<template>
  <div class="kickstart-editor">
    <div class="editor-header">
      <div class="form-item">
        <label>模板名称 <span class="required">*</span></label>
        <input v-model="formData.name" type="text" placeholder="请输入模板名称" :class="{ 'input-error': errors.name }" />
        <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
      </div>
      <div class="form-item">
        <label>关联仓库</label>
        <select v-model="formData.repo">
          <option :value="null">无</option>
          <option v-for="r in repos" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
      </div>
    </div>
    <div class="form-item">
      <label>模板内容 <span class="required">*</span></label>
      <textarea
        v-model="formData.content"
        placeholder="请输入 Kickstart 模板内容"
        rows="15"
        class="code-textarea"
        :class="{ 'input-error': errors.content }"
      ></textarea>
      <span v-if="errors.content" class="field-error">{{ errors.content }}</span>
    </div>
    <div class="form-item">
      <label>内核参数 (JSON)</label>
      <input v-model="formData.kernel_options_json" type="text" placeholder='{"ksdevice": "eth0", "inst.stage2": "..."}' />
    </div>
  </div>
</template>

<script>
import { getRepos } from '@/api/osdeploy/repo'

export default {
  name: 'KickstartEditor',
  props: {
    kickstart: {
      type: Object,
      default: null
    }
  },
  emits: ['update:formData'],
  data() {
    return {
      repos: [],
      formData: {
        name: '',
        repo: null,
        content: '',
        kernel_options_json: ''
      },
      errors: {}
    }
  },
  watch: {
    formData: {
      handler(val) {
        this.$emit('update:formData', val)
      },
      deep: true
    }
  },
  async mounted() {
    await this.loadRepos()
    if (this.kickstart) {
      this.formData = {
        name: this.kickstart.name,
        repo: this.kickstart.repo,
        content: this.kickstart.content,
        kernel_options_json: this.kickstart.kernel_options ? JSON.stringify(this.kickstart.kernel_options) : ''
      }
    }
  },
  methods: {
    async loadRepos() {
      try {
        const res = await getRepos({ page_size: 100 })
        this.repos = res.results || res || []
      } catch (e) {
        console.error('加载仓库列表失败', e)
      }
    },
    validate() {
      this.errors = {}
      if (!this.formData.name.trim()) {
        this.errors.name = '请输入模板名称'
        return false
      }
      if (!this.formData.content.trim()) {
        this.errors.content = '请输入模板内容'
        return false
      }
      return true
    },
    getData() {
      const data = { ...this.formData }
      if (!data.repo) data.repo = null
      if (data.kernel_options_json) {
        try {
          data.kernel_options = JSON.parse(data.kernel_options_json)
        } catch (e) {
          data.kernel_options = {}
        }
      } else {
        data.kernel_options = {}
      }
      delete data.kernel_options_json
      return data
    }
  }
}
</script>

<style scoped>
.kickstart-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.editor-header {
  display: flex;
  gap: 16px;
}

.editor-header .form-item {
  flex: 1;
  margin-bottom: 0;
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
  font-family: inherit;
}

.form-item textarea {
  resize: vertical;
}

.code-textarea {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.required {
  color: #f56c6c;
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
</style>