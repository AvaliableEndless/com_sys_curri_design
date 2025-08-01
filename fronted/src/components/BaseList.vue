<template>
  <div class="base-list">
    <div class="header">
      <h3>{{ title }}</h3>
      <el-button type="primary" @click="$emit('add')" v-if="showAdd">添加</el-button>
    </div>

    <!-- 搜索表单 -->
    <el-form :inline="true" v-if="$slots.search">
      <slot name="search"></slot>
      <el-form-item>
        <el-button type="primary" @click="$emit('search')">搜索</el-button>
        <el-button @click="$emit('reset')">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 数据表格 -->
    <el-table :data="data" border v-loading="loading" style="width: 100%">
      <slot></slot>
    </el-table>

    <!-- 分页 -->
    <div class="pagination" v-if="showPagination">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="$emit('size-change', $event)"
        @current-change="$emit('current-change', $event)"
        @update:current-page="$emit('update:current-page', $event)"
        @update:page-size="$emit('update:page-size', $event)"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  data: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  showAdd: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  currentPage: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    required: true
  },
  total: {
    type: Number,
    required: true
  }
})

defineEmits([
  'add', 
  'search', 
  'reset', 
  'size-change', 
  'current-change',
  'update:current-page',
  'update:page-size'
])
</script>

<style scoped>
.base-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 