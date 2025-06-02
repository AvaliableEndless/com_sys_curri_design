<template>
  <div class="owner-list">
    <div class="search-bar">
      <el-input
        v-model="searchForm.name"
        placeholder="业主姓名"
        clearable
        @clear="handleSearch"
      />
      <el-input
        v-model="searchForm.phone"
        placeholder="手机号码"
        clearable
        @clear="handleSearch"
      />
      <el-input
        v-model="searchForm.number"
        placeholder="业主编号"
        clearable
        @clear="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button type="success" @click="handleAdd">添加业主</el-button>
    </div>

    <el-table :data="ownerList" border style="width: 100%">
      <el-table-column prop="number" label="业主编号" width="120" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="gender" label="性别" width="80">
        <template #default="scope">
          {{ scope.row.gender === '男' ? '男' : '女' }}
        </template>
      </el-table-column>
      <el-table-column prop="age" label="年龄" width="80" />
      <el-table-column prop="phone" label="手机号码" width="150" />
      <el-table-column prop="id_card" label="身份证号" width="180" />
      <el-table-column label="关联房屋" min-width="200">
        <template #default="scope">
          <el-tag
            v-for="house in scope.row.houses"
            :key="house.id"
            class="house-tag"
          >
            {{ house.number }} - {{ house.house_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button
            type="primary"
            size="small"
            @click="handleEdit(scope.row)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />

    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加业主' : '编辑业主'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="业主编号" prop="number">
          <el-input v-model="form.number" placeholder="请输入业主编号" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="1" :max="120" />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="form.idCard" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="关联房屋" prop="houses">
          <el-select
            v-model="form.houses"
            multiple
            filterable
            placeholder="请选择关联房屋"
            style="width: 100%"
          >
            <el-option
              v-for="house in houseOptions"
              :key="house.id"
              :label="`${house.number} - ${house.house_type}`"
              :value="house.id"
            >
              <span>{{ house.number }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ house.house_type }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ownerAPI, houseAPI } from '@/api'

const ownerList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref(null)
const houseOptions = ref([])

const searchForm = reactive({
  name: '',
  phone: '',
  number: ''
})

const form = reactive({
  id: null,
  number: '',
  name: '',
  gender: '男',
  age: 18,
  phone: '',
  idCard: '',
  houses: []
})

const rules = {
  number: [
    { required: true, message: '请输入业主编号', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        
        // 检查是否包含特殊字符
        if (/[^\w\u4e00-\u9fa5-]/.test(value)) {
          callback(new Error('业主编号只能包含字母、数字、中文、下划线和横杠'))
          return
        }
        
        if (dialogType.value === 'add') {
          // 添加时检查编号是否已存在
          const isExist = ownerList.value.some(owner => owner.number === value)
          if (isExist) {
            callback(new Error('业主编号已存在'))
          } else {
            callback()
          }
        } else {
          // 编辑时检查编号是否与其他业主重复
          const isExist = ownerList.value.some(owner => 
            owner.number === value && owner.id !== form.id
          )
          if (isExist) {
            callback(new Error('业主编号已存在'))
          } else {
            callback()
          }
        }
      },
      trigger: 'blur'
    }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  houses: [
    { required: true, message: '请选择关联房屋', trigger: 'change' }
  ]
}

const fetchData = async () => {
  try {
    const res = await ownerAPI.getList({
      page: currentPage.value,
      size: pageSize.value,
      name: searchForm.name,
      phone: searchForm.phone,
      number: searchForm.number
    })
    ownerList.value = res.data
    total.value = res.total
  } catch (error) {
    ElMessage.error('获取业主列表失败')
  }
}

const fetchHouseOptions = async () => {
  try {
    const res = await houseAPI.getList({
      page: 1,
      size: 1000  // 获取所有房屋
    })
    houseOptions.value = res.data
  } catch (error) {
    ElMessage.error('获取房屋列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

const resetForm = () => {
  form.id = null
  form.number = ''
  form.name = ''
  form.gender = '男'
  form.age = 18
  form.phone = ''
  form.idCard = ''
  form.houses = []
}

const handleAdd = () => {
  dialogType.value = 'add'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(form, {
    id: row.id,
    number: row.number,
    name: row.name,
    gender: row.gender,
    age: row.age,
    phone: row.phone,
    idCard: row.id_card,
    houses: row.houses?.map(house => {
      const houseOption = houseOptions.value.find(h => h.number === house.number)
      return houseOption?.id
    }).filter(Boolean) || []
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该业主吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await ownerAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          number: form.number,
          name: form.name,
          gender: form.gender,
          age: form.age,
          phone: form.phone,
          idCard: form.idCard,
          house_numbers: form.houses.map(houseId => {
            const house = houseOptions.value.find(h => h.id === houseId)
            return house.number
          })
        }
        if (dialogType.value === 'add') {
          await ownerAPI.add(data)
          ElMessage.success('添加成功')
        } else {
          // 编辑时，如果业主编号没有变化，也要允许更新
          await ownerAPI.update(form.id, data)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error(dialogType.value === 'add' ? '添加失败:' : '更新失败:', error)
        ElMessage.error(error.response?.data?.message || (dialogType.value === 'add' ? '添加失败' : '更新失败'))
      }
    }
  })
}

onMounted(() => {
  fetchData()
  fetchHouseOptions()
})
</script>

<style scoped>
.owner-list {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.house-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 