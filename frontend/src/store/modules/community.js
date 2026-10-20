/**
 * 社区功能 Pinia Store
 * 管理社区页面的状态：知识库广场、模板广场、分享码导入等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as communityApi from '@/services/community'

export const useCommunityStore = defineStore('community', () => {
  // ── Tab 状态 ──
  const activeTab = ref('kb') // 'kb' | 'template'

  // ── 知识库广场 ──
  const kbList = ref([])
  const kbTotal = ref(0)
  const kbLoading = ref(false)
  const kbPage = ref(1)
  const kbPageSize = ref(12)
  const kbSearch = ref('')
  const kbTagFilter = ref('')
  const kbSort = ref('latest') // latest | popular

  // ── 模板广场 ──
  const templateList = ref([])
  const templateTotal = ref(0)
  const templateLoading = ref(false)
  const templatePage = ref(1)
  const templatePageSize = ref(21)
  const templateSearch = ref('')
  const templateCategory = ref('')
  const templateSort = ref('popular') // popular | latest | downloads

  // ── 分享码弹窗 ──
  const showImportDialog = ref(false)
  const importCode = ref('')
  const importLoading = ref(false)
  const importPreview = ref(null) // 预览数据

  // ── 详情弹窗 ──
  const showDetailDialog = ref(false)
  const detailData = ref(null)
  const detailType = ref('') // 'kb' | 'template'

  // ── 我的分享 ──
  const myShares = ref([])
  const showMyShares = ref(false)

  // ── 我的知识库文件权限管理（模拟） ──
  const myKbFiles = ref([
    {
      id: 'my_file_001',
      file_name: '高一数学-函数概念.pdf',
      visibility: 'private', // private | shared | public
      share_code: null,
      updated_at: '2026-04-14T08:20:00Z'
    },
    {
      id: 'my_file_002',
      file_name: '英语四级核心词汇.xlsx',
      visibility: 'shared',
      share_code: 'KB-S8K2M4Q1',
      updated_at: '2026-04-13T12:10:00Z'
    },
    {
      id: 'my_file_003',
      file_name: '机器学习入门讲义.docx',
      visibility: 'public',
      share_code: 'KB-P7A3V9C2',
      updated_at: '2026-04-12T15:45:00Z'
    }
  ])

  // ── 热门标签 ──
  const hotTags = ref([])

  // ── 社区统计 ──
  const stats = ref({
    kbCount: 0,
    templateCount: 0,
    userCount: 0
  })

  // ── Mock 数据 ──
  const mockKbList = [
    {
      id: 'kb_001',
      share_code: 'KB-A3F9X2K8',
      name: '高中数学必修一知识点',
      description: '涵盖集合、函数、指数函数、对数函数、幂函数等核心知识点，适合高一学生复习使用。',
      author: { id: 'u1', name: '李老师', avatar: '' },
      document_count: 12,
      visibility: 'public',
      import_count: 156,
      tags: ['高中数学', '必修一', '函数', '集合'],
      created_at: '2026-03-15T10:30:00Z',
      file_types: ['pdf', 'docx']
    },
    {
      id: 'kb_002',
      share_code: 'KB-B7M2P4R1',
      name: '大学英语四级词汇库',
      description: '包含CET-4核心词汇4500+，按频率分级，附带例句和用法说明。',
      author: { id: 'u2', name: '王教授', avatar: '' },
      document_count: 8,
      visibility: 'shared',
      import_count: 342,
      tags: ['英语四级', 'CET-4', '词汇', '大学英语'],
      created_at: '2026-03-10T08:00:00Z',
      file_types: ['pdf', 'xlsx']
    },
    {
      id: 'kb_003',
      share_code: 'KB-C9K5N8T3',
      name: 'Python编程入门到进阶',
      description: '从基础语法到面向对象编程，再到Web开发入门，适合零基础学习者。',
      author: { id: 'u3', name: '张工', avatar: '' },
      document_count: 15,
      visibility: 'public',
      import_count: 89,
      tags: ['Python', '编程', '入门', 'Web开发'],
      created_at: '2026-04-01T14:20:00Z',
      file_types: ['pdf', 'md']
    },
    {
      id: 'kb_004',
      share_code: 'KB-D2L6Q9W5',
      name: '中国近代史纲要',
      description: '1840年至今的重要历史事件、人物、条约等，按时间线整理，适合考研复习。',
      author: { id: 'u4', name: '陈老师', avatar: '' },
      document_count: 6,
      visibility: 'private',
      import_count: 67,
      tags: ['近代史', '考研', '历史', '纲要'],
      created_at: '2026-02-28T09:15:00Z',
      file_types: ['pdf', 'docx']
    },
    {
      id: 'kb_005',
      share_code: 'KB-E4N7R2Y8',
      name: '机器学习算法笔记',
      description: '涵盖线性回归、决策树、SVM、神经网络等经典算法原理与实现。',
      author: { id: 'u5', name: '刘博士', avatar: '' },
      document_count: 20,
      visibility: 'public',
      import_count: 234,
      tags: ['机器学习', 'AI', '算法', '深度学习'],
      created_at: '2026-03-22T16:45:00Z',
      file_types: ['pdf', 'md', 'ipynb']
    },
    {
      id: 'kb_006',
      share_code: 'KB-F6P9S4Z1',
      name: '高中物理力学专题',
      description: '牛顿运动定律、动量守恒、能量守恒等力学核心内容，含典型例题。',
      author: { id: 'u6', name: '赵老师', avatar: '' },
      document_count: 9,
      visibility: 'shared',
      import_count: 123,
      tags: ['高中物理', '力学', '牛顿定律', '必修'],
      created_at: '2026-04-05T11:00:00Z',
      file_types: ['pdf', 'docx']
    },
    {
      id: 'kb_007',
      share_code: 'KB-G8Q1T6A3',
      name: '日语N2语法大全',
      description: '日语能力考试N2级别全部语法条目，附例句和中文翻译。',
      author: { id: 'u7', name: '小林', avatar: '' },
      document_count: 11,
      visibility: 'public',
      import_count: 78,
      tags: ['日语', 'N2', '语法', 'JLPT'],
      created_at: '2026-03-18T13:30:00Z',
      file_types: ['pdf']
    },
    {
      id: 'kb_008',
      share_code: 'KB-H2R4U8B6',
      name: '数据分析实战案例集',
      description: '包含电商、金融、社交等多个领域的数据分析案例，使用Python+Pandas实现。',
      author: { id: 'u8', name: '孙分析师', avatar: '' },
      document_count: 14,
      visibility: 'public',
      import_count: 198,
      tags: ['数据分析', 'Python', 'Pandas', '实战'],
      created_at: '2026-04-08T10:00:00Z',
      file_types: ['ipynb', 'pdf', 'csv']
    }
  ]

  const mockTemplateList = [
    {
      id: 'tpl_2018_5129',
      name: '创意新员工入职培训PPT模板',
      description: '动态 - 25页',
      author: { id: 'u1', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/181011/1-1Q0110355280-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/5129.html',
      motion_type: '动态',
      download_count: 203389,
      like_count: 0,
      is_liked: false,
      tags: ['入职培训', '创意'],
      created_at: '2026-04-01T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2019_5620',
      name: '插画风唯美文艺森系PPT模板',
      description: '动态 - 26页',
      author: { id: 'u2', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/190619/1-1Z61Z929180-L.jpg',
      source_url: 'https://www.ypppt.com/article/2019/5620.html',
      motion_type: '动态',
      download_count: 126068,
      like_count: 0,
      is_liked: false,
      tags: ['插画', '文艺'],
      created_at: '2026-04-02T10:00:00Z',
      slide_count: 26
    },
    {
      id: 'tpl_2017_4195',
      name: '简约彩色多用途PPT模板',
      description: '动态 - 25页',
      author: { id: 'u3', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170807/1-1FPF91G80-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4195.html',
      motion_type: '动态',
      download_count: 83134,
      like_count: 0,
      is_liked: false,
      tags: ['简约', '多用途'],
      created_at: '2026-04-03T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2017_4078',
      name: '水墨晕染工作汇报PPT模板',
      description: '静态 - 32页',
      author: { id: 'u4', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170520/1-1F5200S3110-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4078.html',
      motion_type: '静态',
      download_count: 75457,
      like_count: 0,
      is_liked: false,
      tags: ['水墨', '汇报'],
      created_at: '2026-04-04T10:00:00Z',
      slide_count: 32
    },
    {
      id: 'tpl_2021_7247',
      name: '渐变色个人求职简历PPT模板',
      description: '动态 - 20页',
      author: { id: 'u5', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/210302/1-210302104R80-L.jpg',
      source_url: 'https://www.ypppt.com/article/2021/7247.html',
      motion_type: '动态',
      download_count: 74008,
      like_count: 0,
      is_liked: false,
      tags: ['求职', '简历'],
      created_at: '2026-04-05T10:00:00Z',
      slide_count: 20
    },
    {
      id: 'tpl_2020_5819',
      name: '极简红蓝复古论文答辩PPT模板',
      description: '动态 - 27页',
      author: { id: 'u6', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200507/1-20050F922480-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/5819.html',
      motion_type: '动态',
      download_count: 377366,
      like_count: 0,
      is_liked: false,
      tags: ['论文答辩', '复古'],
      created_at: '2026-04-06T10:00:00Z',
      slide_count: 27
    },
    {
      id: 'tpl_2018_4938',
      name: '炫彩水彩晕染通用PPT模板',
      description: '动态 - 24页',
      author: { id: 'u7', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180723/1-1PH30T2350-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4938.html',
      motion_type: '动态',
      download_count: 147353,
      like_count: 0,
      is_liked: false,
      tags: ['水彩', '通用'],
      created_at: '2026-04-07T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2018_5277',
      name: '缤纷彩色方块通用PPT模板',
      description: '动态 - 24页',
      author: { id: 'u8', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/181114/1-1Q1140SI10-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/5277.html',
      motion_type: '动态',
      download_count: 216747,
      like_count: 0,
      is_liked: false,
      tags: ['彩色', '通用'],
      created_at: '2026-04-08T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2018_4713',
      name: '创意墨迹总结计划PPT模板',
      description: '静态 - 30页',
      author: { id: 'u9', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180309/1-1P3091055580-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4713.html',
      motion_type: '静态',
      download_count: 194781,
      like_count: 0,
      is_liked: false,
      tags: ['总结', '计划'],
      created_at: '2026-04-09T10:00:00Z',
      slide_count: 30
    },
    {
      id: 'tpl_2018_5306',
      name: '大气实用年度总结汇报PPT模板',
      description: '动态 - 30页',
      author: { id: 'u10', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/181126/1-1Q1260R3230-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/5306.html',
      motion_type: '动态',
      download_count: 243650,
      like_count: 0,
      is_liked: false,
      tags: ['年度总结', '汇报'],
      created_at: '2026-04-10T10:00:00Z',
      slide_count: 30
    },
    {
      id: 'tpl_2017_4365',
      name: '唯美花朵文艺范报告PPT模板',
      description: '动态 - 26页',
      author: { id: 'u11', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/171028/1-1G02PHF60-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4365.html',
      motion_type: '动态',
      download_count: 124050,
      like_count: 0,
      is_liked: false,
      tags: ['花朵', '文艺'],
      created_at: '2026-04-11T10:00:00Z',
      slide_count: 26
    },
    {
      id: 'tpl_2017_3771',
      name: '同学聚会青春回忆相册PPT模板',
      description: '动态 - 16页',
      author: { id: 'u12', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170308/1-1F30P434300-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/3771.html',
      motion_type: '动态',
      download_count: 70627,
      like_count: 0,
      is_liked: false,
      tags: ['相册', '青春回忆'],
      created_at: '2026-04-12T10:00:00Z',
      slide_count: 16
    },
    {
      id: 'tpl_2018_4786',
      name: '大气商务项目汇报PPT模板',
      description: '动态 - 25页',
      author: { id: 'u13', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180502/1-1P5020934300-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4786.html',
      motion_type: '动态',
      download_count: 213554,
      like_count: 0,
      is_liked: false,
      tags: ['商务', '项目汇报'],
      created_at: '2026-04-13T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2017_3864',
      name: '个性素雅简约黑白PPT模板',
      description: '动态 - 28页',
      author: { id: 'u14', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170324/1-1F3240101040-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/3864.html',
      motion_type: '动态',
      download_count: 95151,
      like_count: 0,
      is_liked: false,
      tags: ['黑白', '简约'],
      created_at: '2026-04-14T10:00:00Z',
      slide_count: 28
    },
    {
      id: 'tpl_2017_4140',
      name: '大方极简商务通用PPT模板',
      description: '动态 - 25页',
      author: { id: 'u15', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170630/1-1F6300U0090-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4140.html',
      motion_type: '动态',
      download_count: 136764,
      like_count: 0,
      is_liked: false,
      tags: ['商务', '极简'],
      created_at: '2026-04-15T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2021_7158',
      name: '雅致远山群山国风意境PPT模板',
      description: '动态 - 24页',
      author: { id: 'u16', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/210224/1-2102240225170-L.jpg',
      source_url: 'https://www.ypppt.com/article/2021/7158.html',
      motion_type: '动态',
      download_count: 230322,
      like_count: 0,
      is_liked: false,
      tags: ['国风', '意境'],
      created_at: '2026-04-16T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2020_6286',
      name: '炫彩烟雾水彩总结述职PPT模板',
      description: '动态 - 48页',
      author: { id: 'u17', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200707/1-200FH333250-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/6286.html',
      motion_type: '动态',
      download_count: 132982,
      like_count: 0,
      is_liked: false,
      tags: ['水彩', '述职'],
      created_at: '2026-04-17T10:00:00Z',
      slide_count: 48
    },
    {
      id: 'tpl_2020_5980',
      name: '素雅简约毕业论文答辩PPT模板',
      description: '动态 - 31页',
      author: { id: 'u18', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200602/1-2006020602160-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/5980.html',
      motion_type: '动态',
      download_count: 460571,
      like_count: 0,
      is_liked: false,
      tags: ['论文答辩', '毕业'],
      created_at: '2026-04-18T10:00:00Z',
      slide_count: 31
    },
    {
      id: 'tpl_2017_3531',
      name: '大方实用毕业论文答辩PPT模板',
      description: '静态 - 30页',
      author: { id: 'u19', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170126/1-1F126110I9215.jpg',
      source_url: 'https://www.ypppt.com/article/2017/3531.html',
      motion_type: '静态',
      download_count: 280099,
      like_count: 0,
      is_liked: false,
      tags: ['毕业论文', '答辩'],
      created_at: '2026-04-19T10:00:00Z',
      slide_count: 30
    },
    {
      id: 'tpl_2017_4292',
      name: '淡雅简约工作总结报告PPT模板',
      description: '动态 - 24页',
      author: { id: 'u20', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/171011/1-1G0110ZK40-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4292.html',
      motion_type: '动态',
      download_count: 225272,
      like_count: 0,
      is_liked: false,
      tags: ['工作总结', '报告'],
      created_at: '2026-04-20T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2018_4826',
      name: '毕业季动态电子相册PPT模板',
      description: '动态 - 20页',
      author: { id: 'u21', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180612/1-1P612132H20-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4826.html',
      motion_type: '动态',
      download_count: 106523,
      like_count: 0,
      is_liked: false,
      tags: ['毕业季', '电子相册'],
      created_at: '2026-04-21T10:00:00Z',
      slide_count: 20
    },
    {
      id: 'tpl_2019_5695',
      name: '唯美可爱卡通动物PPT模板',
      description: '动态 - 23页',
      author: { id: 'u22', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/191030/1-1910300630000-L.jpg',
      source_url: 'https://www.ypppt.com/article/2019/5695.html',
      motion_type: '动态',
      download_count: 191583,
      like_count: 0,
      is_liked: false,
      tags: ['卡通', '动物'],
      created_at: '2026-04-22T10:00:00Z',
      slide_count: 23
    },
    {
      id: 'tpl_2017_4203',
      name: '时尚创意欧美范商务PPT模板',
      description: '动态 - 25页',
      author: { id: 'u23', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170822/1-1FR20TK70-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4203.html',
      motion_type: '动态',
      download_count: 162251,
      like_count: 0,
      is_liked: false,
      tags: ['欧美范', '商务'],
      created_at: '2026-04-23T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2017_4136',
      name: '素描手绘旅游旅行主题PPT模板',
      description: '动态 - 25页',
      author: { id: 'u24', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170629/1-1F62Z931560-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4136.html',
      motion_type: '动态',
      download_count: 146912,
      like_count: 0,
      is_liked: false,
      tags: ['手绘', '旅行'],
      created_at: '2026-04-24T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2022_14914',
      name: '简约时尚清新绿粉圆点PPT模板',
      description: '动态 - 25页',
      author: { id: 'u25', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/221229/1-2212291522410-L.jpg',
      source_url: 'https://www.ypppt.com/article/2022/14914.html',
      motion_type: '动态',
      download_count: 48953,
      like_count: 0,
      is_liked: false,
      tags: ['清新', '圆点'],
      created_at: '2026-04-25T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2020_5842',
      name: '上半年总结下半年计划PPT模板',
      description: '动态 - 36页',
      author: { id: 'u26', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200515/1-2005151256360-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/5842.html',
      motion_type: '动态',
      download_count: 183639,
      like_count: 0,
      is_liked: false,
      tags: ['总结', '计划'],
      created_at: '2026-04-26T10:00:00Z',
      slide_count: 36
    },
    {
      id: 'tpl_2018_4703',
      name: '简约雅致圆圈泡泡通用PPT模板',
      description: '动态 - 17页',
      author: { id: 'u27', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180305/1-1P3050QR10-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4703.html',
      motion_type: '动态',
      download_count: 305974,
      like_count: 0,
      is_liked: false,
      tags: ['简约', '通用'],
      created_at: '2026-04-27T10:00:00Z',
      slide_count: 17
    },
    {
      id: 'tpl_2019_5594',
      name: '极简灰黑公司介绍PPT模板',
      description: '动态 - 24页',
      author: { id: 'u28', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/190508/1-1Z50PU6330-L.jpg',
      source_url: 'https://www.ypppt.com/article/2019/5594.html',
      motion_type: '动态',
      download_count: 138140,
      like_count: 0,
      is_liked: false,
      tags: ['公司介绍', '极简'],
      created_at: '2026-04-28T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2018_4588',
      name: '大气极简深蓝通用PPT模板',
      description: '动态 - 24页',
      author: { id: 'u29', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180119/1-1P11Z914190-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4588.html',
      motion_type: '动态',
      download_count: 140797,
      like_count: 0,
      is_liked: false,
      tags: ['深蓝', '通用'],
      created_at: '2026-04-29T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2019_5679',
      name: '简洁时尚渐变通用PPT模板',
      description: '动态 - 25页',
      author: { id: 'u30', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/191009/1-19100ZF5380-L.jpg',
      source_url: 'https://www.ypppt.com/article/2019/5679.html',
      motion_type: '动态',
      download_count: 87964,
      like_count: 0,
      is_liked: false,
      tags: ['渐变', '通用'],
      created_at: '2026-04-30T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2017_4425',
      name: '立体动感缤纷三角形PPT模板',
      description: '动态 - 29页',
      author: { id: 'u31', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/171108/1-1G10R303420-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4425.html',
      motion_type: '动态',
      download_count: 112008,
      like_count: 0,
      is_liked: false,
      tags: ['三角形', '动感'],
      created_at: '2026-05-01T10:00:00Z',
      slide_count: 29
    },
    {
      id: 'tpl_2016_2919',
      name: '时尚精美复古英伦风PPT模板',
      description: '动态 - 27页',
      author: { id: 'u32', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/160908/1-160ZP91I2-lp.jpg',
      source_url: 'https://www.ypppt.com/article/2016/2919.html',
      motion_type: '动态',
      download_count: 93392,
      like_count: 0,
      is_liked: false,
      tags: ['英伦风', '复古'],
      created_at: '2026-05-02T10:00:00Z',
      slide_count: 27
    },
    {
      id: 'tpl_2018_4656',
      name: '卡通黑板教育教学课件PPT模板',
      description: '动态 - 24页',
      author: { id: 'u33', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180209/1-1P20Z919390-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4656.html',
      motion_type: '动态',
      download_count: 132490,
      like_count: 0,
      is_liked: false,
      tags: ['教育', '课件'],
      created_at: '2026-05-03T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2017_3720',
      name: '精美西餐厅西餐PPT模板下载',
      description: '动态 - 23页',
      author: { id: 'u34', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170301/1-1F3010313450-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/3720.html',
      motion_type: '动态',
      download_count: 84338,
      like_count: 0,
      is_liked: false,
      tags: ['西餐', '餐厅'],
      created_at: '2026-05-04T10:00:00Z',
      slide_count: 23
    },
    {
      id: 'tpl_2017_4164',
      name: '清爽淡雅水彩花卉PPT模板',
      description: '动态 - 25页',
      author: { id: 'u35', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170706/1-1FF60Z3030-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4164.html',
      motion_type: '动态',
      download_count: 101158,
      like_count: 0,
      is_liked: false,
      tags: ['水彩', '花卉'],
      created_at: '2026-05-05T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2022_14200',
      name: '清新蓝工作总结汇报PPT模板',
      description: '动态 - 22页',
      author: { id: 'u36', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/220531/1-2205311K3580-L.jpg',
      source_url: 'https://www.ypppt.com/article/2022/14200.html',
      motion_type: '动态',
      download_count: 217091,
      like_count: 0,
      is_liked: false,
      tags: ['工作总结', '汇报'],
      created_at: '2026-05-06T10:00:00Z',
      slide_count: 22
    },
    {
      id: 'tpl_2021_9320',
      name: '简约清新项目汇报PPT模板',
      description: '动态 - 21页',
      author: { id: 'u37', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/210908/1-210ZPQ6450-L.jpg',
      source_url: 'https://www.ypppt.com/article/2021/9320.html',
      motion_type: '动态',
      download_count: 301463,
      like_count: 0,
      is_liked: false,
      tags: ['项目汇报', '简约'],
      created_at: '2026-05-07T10:00:00Z',
      slide_count: 21
    },
    {
      id: 'tpl_2021_7713',
      name: '清新简约手绘桌面通用PPT模板',
      description: '动态 - 25页',
      author: { id: 'u38', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/210427/1-21042G102010-L.jpg',
      source_url: 'https://www.ypppt.com/article/2021/7713.html',
      motion_type: '动态',
      download_count: 157370,
      like_count: 0,
      is_liked: false,
      tags: ['手绘', '通用'],
      created_at: '2026-05-08T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2016_2698',
      name: '实用创业商业计划书PPT模板',
      description: '动态 - 32页',
      author: { id: 'u39', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/160506/1-160506092115-lp.jpg',
      source_url: 'https://www.ypppt.com/article/2016/2698.html',
      motion_type: '动态',
      download_count: 92481,
      like_count: 0,
      is_liked: false,
      tags: ['创业', '商业计划书'],
      created_at: '2026-05-09T10:00:00Z',
      slide_count: 32
    },
    {
      id: 'tpl_2017_4206',
      name: '淡雅唯美花卉通用PPT模板',
      description: '动态 - 26页',
      author: { id: 'u40', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170823/1-1FR30Z3130-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4206.html',
      motion_type: '动态',
      download_count: 81966,
      like_count: 0,
      is_liked: false,
      tags: ['花卉', '唯美'],
      created_at: '2026-05-10T10:00:00Z',
      slide_count: 26
    },
    {
      id: 'tpl_2018_5060',
      name: '淡雅文艺自然小清新PPT模板',
      description: '动态 - 24页',
      author: { id: 'u41', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180914/1-1P9140224250-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/5060.html',
      motion_type: '动态',
      download_count: 123038,
      like_count: 0,
      is_liked: false,
      tags: ['文艺', '小清新'],
      created_at: '2026-05-11T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2020_5757',
      name: '黑红工作汇报总结PPT模板',
      description: '动态 - 44页',
      author: { id: 'u42', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200307/1-20030H341040-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/5757.html',
      motion_type: '动态',
      download_count: 170012,
      like_count: 0,
      is_liked: false,
      tags: ['工作汇报', '黑红'],
      created_at: '2026-05-12T10:00:00Z',
      slide_count: 44
    },
    {
      id: 'tpl_2017_4066',
      name: '圆角矩形工作总结汇报PPT模板',
      description: '动态 - 23页',
      author: { id: 'u43', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170506/1-1F5061201310-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4066.html',
      motion_type: '动态',
      download_count: 91944,
      like_count: 0,
      is_liked: false,
      tags: ['总结汇报', '圆角矩形'],
      created_at: '2026-05-13T10:00:00Z',
      slide_count: 23
    },
    {
      id: 'tpl_2016_3078',
      name: '建筑土木工程论文答辩PPT模板',
      description: '动态 - 41页',
      author: { id: 'u44', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/161203/1-161203102518-lp.jpg',
      source_url: 'https://www.ypppt.com/article/2016/3078.html',
      motion_type: '动态',
      download_count: 117676,
      like_count: 0,
      is_liked: false,
      tags: ['论文答辩', '土木工程'],
      created_at: '2026-05-14T10:00:00Z',
      slide_count: 41
    },
    {
      id: 'tpl_2021_8700',
      name: '素雅古典花鸟中国风PPT模板',
      description: '动态 - 26页',
      author: { id: 'u45', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/210807/1-210PG222330-L.jpg',
      source_url: 'https://www.ypppt.com/article/2021/8700.html',
      motion_type: '动态',
      download_count: 197279,
      like_count: 0,
      is_liked: false,
      tags: ['中国风', '花鸟'],
      created_at: '2026-05-15T10:00:00Z',
      slide_count: 26
    },
    {
      id: 'tpl_2020_5795',
      name: '莫兰迪色淡雅蒲公英PPT模板',
      description: '动态 - 36页',
      author: { id: 'u46', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200423/1-2004230031470-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/5795.html',
      motion_type: '动态',
      download_count: 131819,
      like_count: 0,
      is_liked: false,
      tags: ['莫兰迪', '蒲公英'],
      created_at: '2026-05-16T10:00:00Z',
      slide_count: 36
    },
    {
      id: 'tpl_2018_4875',
      name: '大气半年工作总结汇报PPT模板',
      description: '动态 - 25页',
      author: { id: 'u47', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180702/1-1PF2101R50-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4875.html',
      motion_type: '动态',
      download_count: 159624,
      like_count: 0,
      is_liked: false,
      tags: ['半年总结', '汇报'],
      created_at: '2026-05-17T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2019_5555',
      name: '大气产品公司介绍PPT模板',
      description: '动态 - 25页',
      author: { id: 'u48', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/190306/1-1Z306005F70-L.jpg',
      source_url: 'https://www.ypppt.com/article/2019/5555.html',
      motion_type: '动态',
      download_count: 163701,
      like_count: 0,
      is_liked: false,
      tags: ['公司介绍', '产品'],
      created_at: '2026-05-18T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2018_4784',
      name: '淡雅简洁中国风PPT模板',
      description: '动态 - 25页',
      author: { id: 'u49', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180426/1-1P4260911480-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4784.html',
      motion_type: '动态',
      download_count: 237396,
      like_count: 0,
      is_liked: false,
      tags: ['中国风', '淡雅'],
      created_at: '2026-05-19T10:00:00Z',
      slide_count: 25
    },
    {
      id: 'tpl_2019_5644',
      name: '简约黑色三角几何通用PPT模板',
      description: '动态 - 22页',
      author: { id: 'u50', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/190802/1-1ZP21645050-L.jpg',
      source_url: 'https://www.ypppt.com/article/2019/5644.html',
      motion_type: '动态',
      download_count: 116084,
      like_count: 0,
      is_liked: false,
      tags: ['三角几何', '黑色'],
      created_at: '2026-05-20T10:00:00Z',
      slide_count: 22
    },
    {
      id: 'tpl_2018_4695',
      name: '卡通热气球教学课件PPT模板',
      description: '静态 - 20页',
      author: { id: 'u51', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180302/1-1P3020919100-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4695.html',
      motion_type: '静态',
      download_count: 199592,
      like_count: 0,
      is_liked: false,
      tags: ['教学课件', '热气球'],
      created_at: '2026-05-21T10:00:00Z',
      slide_count: 20
    },
    {
      id: 'tpl_2015_1749',
      name: '旅游景点行程介绍PPT模板',
      description: '静态 - 16页',
      author: { id: 'u52', name: '社区用户', avatar: '' },
      category: 'art',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/150911/1-150911102S7-lp.jpg',
      source_url: 'https://www.ypppt.com/article/2015/1749.html',
      motion_type: '静态',
      download_count: 170522,
      like_count: 0,
      is_liked: false,
      tags: ['旅游', '景点'],
      created_at: '2026-05-22T10:00:00Z',
      slide_count: 16
    },
    {
      id: 'tpl_2018_4812',
      name: '插画风儿童教学课件PPT模板',
      description: '动态 - 24页',
      author: { id: 'u53', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180531/1-1P5310TU00-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4812.html',
      motion_type: '动态',
      download_count: 204308,
      like_count: 0,
      is_liked: false,
      tags: ['儿童', '教学课件'],
      created_at: '2026-05-23T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2016_2321',
      name: '精美低碳节能绿色环保PPT模板',
      description: '动态 - 38页',
      author: { id: 'u54', name: '社区用户', avatar: '' },
      category: 'education',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/160227/1-16022G31401-lp.jpg',
      source_url: 'https://www.ypppt.com/article/2016/2321.html',
      motion_type: '动态',
      download_count: 97690,
      like_count: 0,
      is_liked: false,
      tags: ['环保', '低碳'],
      created_at: '2026-05-24T10:00:00Z',
      slide_count: 38
    },
    {
      id: 'tpl_2017_4063',
      name: '清新蓝粉方块通用PPT模板',
      description: '动态 - 24页',
      author: { id: 'u55', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/170504/1-1F5040025090-L.jpg',
      source_url: 'https://www.ypppt.com/article/2017/4063.html',
      motion_type: '动态',
      download_count: 189182,
      like_count: 0,
      is_liked: false,
      tags: ['蓝粉', '通用'],
      created_at: '2026-05-25T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2021_7900',
      name: '大气极简工作述职报告PPT模板',
      description: '动态 - 24页',
      author: { id: 'u56', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/210514/1-2105141134150-L.jpg',
      source_url: 'https://www.ypppt.com/article/2021/7900.html',
      motion_type: '动态',
      download_count: 200198,
      like_count: 0,
      is_liked: false,
      tags: ['述职报告', '极简'],
      created_at: '2026-05-26T10:00:00Z',
      slide_count: 24
    },
    {
      id: 'tpl_2020_6360',
      name: '简约通用工作总结计划PPT模板',
      description: '动态 - 31页',
      author: { id: 'u57', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200723/1-200H31309370-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/6360.html',
      motion_type: '动态',
      download_count: 215259,
      like_count: 0,
      is_liked: false,
      tags: ['总结计划', '通用'],
      created_at: '2026-05-27T10:00:00Z',
      slide_count: 31
    },
    {
      id: 'tpl_2020_6316',
      name: '欧美范杂志风图文排版PPT模板',
      description: '动态 - 26页',
      author: { id: 'u58', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/200715/1-200G5120F80-L.jpg',
      source_url: 'https://www.ypppt.com/article/2020/6316.html',
      motion_type: '动态',
      download_count: 133279,
      like_count: 0,
      is_liked: false,
      tags: ['欧美范', '杂志风'],
      created_at: '2026-05-28T10:00:00Z',
      slide_count: 26
    },
    {
      id: 'tpl_2015_917',
      name: '精美实用总结计划PPT模板',
      description: '静态 - 27页',
      author: { id: 'u59', name: '社区用户', avatar: '' },
      category: 'business',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/150522/1-150522093051-lp.jpg',
      source_url: 'https://www.ypppt.com/article/2015/917.html',
      motion_type: '静态',
      download_count: 121870,
      like_count: 0,
      is_liked: false,
      tags: ['总结计划', '实用'],
      created_at: '2026-05-29T10:00:00Z',
      slide_count: 27
    },
    {
      id: 'tpl_2018_4677',
      name: '清新立方体立体效果PPT模板',
      description: '动态 - 26页',
      author: { id: 'u60', name: '社区用户', avatar: '' },
      category: 'creative',
      thumbnail_url: 'https://www.ypppt.com/uploads/allimg/180224/1-1P2240Z9140-L.jpg',
      source_url: 'https://www.ypppt.com/article/2018/4677.html',
      motion_type: '动态',
      download_count: 94607,
      like_count: 0,
      is_liked: false,
      tags: ['立方体', '立体效果'],
      created_at: '2026-05-30T10:00:00Z',
      slide_count: 26
    }
  ]

  const mockHotTags = [
    { name: '教育', count: 234 },
    { name: 'Python', count: 189 },
    { name: '高中数学', count: 156 },
    { name: '学术', count: 134 },
    { name: '科技', count: 112 },
    { name: '考研', count: 98 },
    { name: '数据分析', count: 87 },
    { name: '英语', count: 76 },
    { name: '机器学习', count: 65 },
    { name: '创意', count: 54 }
  ]

  // ── 计算属性 ──
  const filteredKbList = computed(() => {
    let list = [...mockKbList]

    // 社区广场仅展示互联网公开内容
    list = list.filter(item => item.visibility === 'public')

    if (kbSearch.value) {
      const kw = kbSearch.value.toLowerCase()
      list = list.filter(item =>
        item.name.toLowerCase().includes(kw) ||
        item.description.toLowerCase().includes(kw) ||
        item.tags.some(t => t.toLowerCase().includes(kw))
      )
    }
    if (kbTagFilter.value) {
      list = list.filter(item => item.tags.includes(kbTagFilter.value))
    }
    if (kbSort.value === 'popular') {
      list.sort((a, b) => b.import_count - a.import_count)
    } else {
      list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }
    kbTotal.value = list.length
    const start = (kbPage.value - 1) * kbPageSize.value
    return list.slice(start, start + kbPageSize.value)
  })

  const filteredTemplateList = computed(() => {
    let list = [...mockTemplateList]
    if (templateSearch.value) {
      const kw = templateSearch.value.toLowerCase()
      list = list.filter(item =>
        item.name.toLowerCase().includes(kw) ||
        item.description.toLowerCase().includes(kw) ||
        item.tags.some(t => t.toLowerCase().includes(kw))
      )
    }
    if (templateCategory.value) {
      list = list.filter(item => item.category === templateCategory.value)
    }
    if (templateSort.value === 'popular') {
      list.sort((a, b) => b.like_count - a.like_count)
    } else if (templateSort.value === 'downloads') {
      list.sort((a, b) => b.download_count - a.download_count)
    } else {
      list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }
    templateTotal.value = list.length
    const start = (templatePage.value - 1) * templatePageSize.value
    return list.slice(start, start + templatePageSize.value)
  })

  // ── Actions ──

  /** 加载知识库广场 */
  async function loadKbList() {
    kbLoading.value = true
    try {
      // TODO: 替换为真实 API
      // const res = await communityApi.exploreKb({ page: kbPage.value, search: kbSearch.value, tag: kbTagFilter.value, sort: kbSort.value })
      // kbList.value = res.data.items
      // kbTotal.value = res.data.total
      await new Promise(r => setTimeout(r, 300))
      kbList.value = filteredKbList.value
    } catch (e) {
      console.error('加载知识库列表失败:', e)
    } finally {
      kbLoading.value = false
    }
  }

  /** 加载模板广场 */
  async function loadTemplateList() {
    templateLoading.value = true
    try {
      // TODO: 替换为真实 API
      await new Promise(r => setTimeout(r, 300))
      templateList.value = filteredTemplateList.value
    } catch (e) {
      console.error('加载模板列表失败:', e)
    } finally {
      templateLoading.value = false
    }
  }

  /** 查询分享码预览 */
  async function previewShareCode(code) {
    importLoading.value = true
    importPreview.value = null
    try {
      // TODO: 替换为真实 API
      await new Promise(r => setTimeout(r, 500))
      // 分享码可命中：仅分享可见 + 互联网公开
      const found = mockKbList.find(kb =>
        kb.share_code === code.toUpperCase() && kb.visibility !== 'private'
      )
      if (found) {
        importPreview.value = { type: 'kb', data: found }
      } else {
        const tplFound = mockTemplateList.find(tpl => tpl.share_code === code.toUpperCase())
        if (tplFound) {
          importPreview.value = { type: 'template', data: tplFound }
        } else {
          importPreview.value = null
          ElMessage.warning('未找到对应的分享内容，请检查分享码')
        }
      }
    } catch (e) {
      ElMessage.error('查询失败，请稍后重试')
    } finally {
      importLoading.value = false
    }
  }

  /** 导入知识库（Mock） */
  async function importKb(shareCode) {
    importLoading.value = true
    try {
      // TODO: 替换为真实 API
      await new Promise(r => setTimeout(r, 1500))
      ElMessage.success('知识库导入成功！已添加到您的知识库中。')
      showImportDialog.value = false
      importCode.value = ''
      importPreview.value = null
    } catch (e) {
      ElMessage.error('导入失败，请稍后重试')
    } finally {
      importLoading.value = false
    }
  }

  /** 下载模板（Mock） */
  async function downloadTemplate(templateId) {
    try {
      // TODO: 替换为真实 API
      await new Promise(r => setTimeout(r, 800))
      const tpl = mockTemplateList.find(t => t.id === templateId)
      if (tpl) {
        tpl.download_count++
        tpl.is_liked = true
      }
      ElMessage.success('模板已保存到您的模板库中！')
    } catch (e) {
      ElMessage.error('下载失败，请稍后重试')
    }
  }

  /** 点赞模板（Mock） */
  function toggleLike(templateId) {
    const tpl = mockTemplateList.find(t => t.id === templateId)
    if (tpl) {
      tpl.is_liked = !tpl.is_liked
      tpl.like_count += tpl.is_liked ? 1 : -1
    }
  }

  /** 加载热门标签 */
  async function loadHotTags() {
    try {
      // TODO: 替换为真实 API
      hotTags.value = mockHotTags
    } catch (e) {
      console.error('加载标签失败:', e)
    }
  }

  /** 打开详情弹窗 */
  function openDetail(type, data) {
    detailType.value = type
    detailData.value = data
    showDetailDialog.value = true
  }

  /** 关闭详情弹窗 */
  function closeDetail() {
    showDetailDialog.value = false
    detailData.value = null
  }

  /** 重置筛选 */
  function resetKbFilter() {
    kbSearch.value = ''
    kbTagFilter.value = ''
    kbSort.value = 'latest'
    kbPage.value = 1
  }

  function resetTemplateFilter() {
    templateSearch.value = ''
    templateCategory.value = ''
    templateSort.value = 'popular'
    templatePage.value = 1
  }

  function generateShareCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    let code = 'KB-'
    for (let i = 0; i < 8; i++) {
      code += chars[Math.floor(Math.random() * chars.length)]
    }
    return code
  }

  function getVisibilityMeta(visibility) {
    if (visibility === 'private') {
      return { label: '私密非公开', tone: 'private' }
    }
    if (visibility === 'shared') {
      return { label: '仅分享可见', tone: 'shared' }
    }
    return { label: '互联网公开', tone: 'public' }
  }

  function updateKbVisibility(fileId, visibility) {
    const target = myKbFiles.value.find(file => file.id === fileId)
    if (!target) return

    target.visibility = visibility
    target.updated_at = new Date().toISOString()

    if (visibility === 'private') {
      target.share_code = null
    } else if (!target.share_code) {
      target.share_code = generateShareCode()
    }

    const visibilityText = getVisibilityMeta(visibility).label
    ElMessage.success(`已更新为：${visibilityText}`)
  }

  return {
    // State
    activeTab,
    kbList, kbTotal, kbLoading, kbPage, kbPageSize, kbSearch, kbTagFilter, kbSort,
    templateList, templateTotal, templateLoading, templatePage, templatePageSize,
    templateSearch, templateCategory, templateSort,
    showImportDialog, importCode, importLoading, importPreview,
    showDetailDialog, detailData, detailType,
    myShares, showMyShares,
    myKbFiles,
    hotTags, stats,
    // Actions
    loadKbList, loadTemplateList,
    previewShareCode, importKb,
    downloadTemplate, toggleLike,
    loadHotTags,
    openDetail, closeDetail,
    resetKbFilter, resetTemplateFilter,
    updateKbVisibility, getVisibilityMeta
  }
})
