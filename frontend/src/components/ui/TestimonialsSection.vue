<template>
  <section ref="sectionRef" class="testimonials-section">
    <div class="testimonials-container">
      <div
        :class="[
          'testimonials-header',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
        ]"
      >
        <h2 class="testimonials-title">听听用户怎么说</h2>
        <p class="testimonials-subtitle">看看我们的用户对我们的评价</p>
      </div>

      <div class="testimonials-grid">
        <TestimonialsColumn :testimonials="firstColumn" :duration="15" />
        <TestimonialsColumn :testimonials="secondColumn" class-name="hidden md:block" :duration="19" />
        <TestimonialsColumn :testimonials="thirdColumn" class-name="hidden lg:block" :duration="17" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import TestimonialsColumn, { type TestimonialItem } from './TestimonialsColumn.vue'

const testimonials: TestimonialItem[] = [
  {
    text: "给本科生的Python教案自动嵌入了LeetCode入门习题，PPT里代码块可直接复制，学生反馈预习效率提升60%。",
    image: "https://randomuser.me/api/portraits/men/10.jpg",
    name: "陈立伟",
    role: "省级教学名师·计算机系副教授",
  },
  {
    text: "生成的传播学概论课件，能自动匹配最新行业报告，案例从传统媒体延伸到短视频平台，课堂讨论活跃度显著提高。",
    image: "https://randomuser.me/api/portraits/women/11.jpg",
    name: "林晓燕",
    role: "新闻传播学院骨干教师",
  },
  {
    text: "机械原理课程的教案，把复杂机构运动做成动态SVG图，学生能直观理解曲柄滑块原理，课后作业错误率下降40%。",
    image: "https://randomuser.me/api/portraits/men/12.jpg",
    name: "王建国",
    role: "校级优秀班主任·机械工程讲师",
  },
  {
    text: "给研究生的比较文学教案，自动梳理了福柯理论在中西方文本中的应用差异，参考文献直接链接到JSTOR数据库。",
    image: "https://randomuser.me/api/portraits/women/13.jpg",
    name: "张曼琪",
    role: "青年学术带头人·比较文学副教授",
  },
  {
    text: "大学英语读写课课件，会根据四六级考纲调整阅读难度，写作模块嵌入AI语法检查工具演示，学生写作平均分提高8分。",
    image: "https://randomuser.me/api/portraits/men/14.jpg",
    name: "刘畅",
    role: "外语教学创新奖获得者",
  },
  {
    text: "生成的宏观经济学教案，实时抓取美联储利率决议等最新数据，IS-LM模型分析直接对接当前经济形势，课堂互动增加。",
    image: "https://randomuser.me/api/portraits/women/15.jpg",
    name: "赵文轩",
    role: "经济学院教学之星·硕士生导师",
  },
  {
    text: "艺术史课程PPT自动按艺术流派时间线排版，名画细节图可放大展示笔触，教案里还附了美术馆虚拟参观链接。",
    image: "https://randomuser.me/api/portraits/women/16.jpg",
    name: "黄雨桐",
    role: "艺术学院青年教学能手",
  },
  {
    text: "计算机网络教案把TCP/IP协议封装过程做成动画演示，实验环节直接提供Wireshark抓包练习指导，学生实验报告完成质量高。",
    image: "https://randomuser.me/api/portraits/men/17.jpg",
    name: "周明远",
    role: "信息技术系主任·教授",
  },
  {
    text: "给大一新生的高等数学教案，把抽象极限概念用分形几何图像辅助理解，课后习题分层设计，兼顾考研和基础薄弱学生。",
    image: "https://randomuser.me/api/portraits/women/18.jpg",
    name: "孙佳琪",
    role: "数学学院最受欢迎教师",
  },
  {
    text: "社会学研究方法教案，自动生成SPSS操作步骤图解，结合当下青年社交行为案例设计问卷，学生实践作业完成效率提升。",
    image: "https://randomuser.me/api/portraits/men/19.jpg",
    name: "郑宇辰",
    role: "社会学系优秀青年学者",
  },
  {
    text: "国际法课程教案实时更新国际法院最新判例，把《联合国海洋法公约》条款和南海仲裁案结合分析，案例时效性强。",
    image: "https://randomuser.me/api/portraits/women/20.jpg",
    name: "吴思瑶",
    role: "法学院教学创新标兵",
  },
  {
    text: "材料力学课件将不同材料的应力应变曲线做成可对比图表，教案里附了3D打印试件的实验设计，学生参与实验积极性高。",
    image: "https://randomuser.me/api/portraits/men/21.jpg",
    name: "马文博",
    role: "工科实验教学模式改革先锋",
  },
  {
    text: "中国现代文学教案，自动梳理了鲁迅作品在不同时期的解读差异，嵌入了《狂人日记》的手稿扫描件对比，拓展深度足够。",
    image: "https://randomuser.me/api/portraits/women/22.jpg",
    name: "朱雨欣",
    role: "文学院教学成果奖获得者",
  },
  {
    text: "环境科学概论课件，实时调取各城市PM2.5监测数据，结合碳中和政策设计案例分析，学生对知识点的现实关联理解深刻。",
    image: "https://randomuser.me/api/portraits/men/23.jpg",
    name: "胡海洋",
    role: "环境科学系学科带头人",
  },
  {
    text: "组织行为学教案，用最新职场调研数据支撑激励理论，设计了95后员工管理的模拟案例，MBA学生课堂讨论参与度高。",
    image: "https://randomuser.me/api/portraits/women/24.jpg",
    name: "郭晓敏",
    role: "商学院MBA最受欢迎教授",
  },
  {
    text: "量子力学导论教案，把薛定谔方程推导过程拆解成动画步骤，用科幻电影片段辅助解释量子隧穿效应，降低入门难度。",
    image: "https://randomuser.me/api/portraits/men/25.jpg",
    name: "高天翔",
    role: "物理学院科普教育先进个人",
  },
  {
    text: "会计学原理课件，根据最新企业会计准则更新会计科目，嵌入了上市公司财报真实案例的分析引导，学生应用能力提升。",
    image: "https://randomuser.me/api/portraits/women/26.jpg",
    name: "蔡文静",
    role: "会计系实践教学改革带头人",
  },
  {
    text: "体育社会学教案，结合电竞入奥等热点事件设计讨论题，自动引用最新体育产业报告数据，内容贴近学生兴趣点。",
    image: "https://randomuser.me/api/portraits/men/27.jpg",
    name: "田浩然",
    role: "体育学院跨学科教学探索者",
  },
  {
    text: "语言学概论课件，用AI语音识别技术演示音位对立，教案里附了不同方言声调对比练习，学生课堂参与互动频繁。",
    image: "https://randomuser.me/api/portraits/women/28.jpg",
    name: "谢雨桐",
    role: "语言学实验室负责人·副教授",
  },
  {
    text: "工程热力学教案，将热力循环过程做成可调节参数的动态模型，学生能直观看到压力变化对效率的影响，理解更透彻。",
    image: "https://randomuser.me/api/portraits/men/29.jpg",
    name: "廖文浩",
    role: "能源工程学院教学卓越奖得主",
  },
]

const firstColumn = computed(() => testimonials.slice(0, 7))
const secondColumn = computed(() => testimonials.slice(7, 14))
const thirdColumn = computed(() => testimonials.slice(14, 20))

const sectionRef = ref<HTMLElement | null>(null)
const isVisible = ref(false)

let observer: IntersectionObserver | null = null

onMounted(() => {
  if (!sectionRef.value) return

  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting) {
        isVisible.value = true
        observer?.disconnect()
      }
    },
    { threshold: 0.1, rootMargin: '0px' }
  )

  observer.observe(sectionRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.testimonials-section {
  background-color: #050505;
  color: #f8fafc;
  padding: 5rem 0;
  position: relative;
}

.testimonials-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.testimonials-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 540px;
  margin: 0 auto 3rem;
  transition-property: opacity, transform;
  transition-duration: 700ms;
  transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}

.testimonials-badge {
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 0.5rem;
  padding: 0.25rem 1rem;
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.testimonials-title {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 1.25rem 0;
  text-align: center;
}

@media (min-width: 768px) {
  .testimonials-title {
    font-size: 3rem;
  }
}

@media (min-width: 1024px) {
  .testimonials-title {
    font-size: 3.75rem;
  }
}

.testimonials-subtitle {
  font-size: 1.125rem;
  margin: 0;
  text-align: center;
  opacity: 0.75;
}

.testimonials-grid {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2.5rem;
  mask-image: linear-gradient(to bottom, transparent, black 25%, black 75%, transparent);
  max-height: 740px;
  overflow: hidden;
}



.testimonials-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 540px;
  margin: 0 auto 3rem;
}

.testimonials-badge {
  border: 1px solid rgba(255, 255, 255, 0.16);
  padding: 0.25rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.testimonials-title {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 1.25rem 0;
  text-align: center;
}

@media (min-width: 768px) {
  .testimonials-title {
    font-size: 3rem;
  }
}

@media (min-width: 1024px) {
  .testimonials-title {
    font-size: 3.75rem;
  }
}

.testimonials-subtitle {
  font-size: 1.125rem;
  margin: 0;
  text-align: center;
  opacity: 0.75;
}

.testimonials-grid {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2.5rem;
  mask-image: linear-gradient(to bottom, transparent, black 25%, black 75%, transparent);
  max-height: 740px;
  overflow: hidden;
}
</style>
