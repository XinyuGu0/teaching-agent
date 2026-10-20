<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { Check, Eye, EyeOff, Lock, Mail, Sparkles, User, X } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const showPassword = ref(false)
const email = ref('')
const password = ref('')
const username = ref('')
const confirmPassword = ref('')
const error = ref('')
const isLoading = ref(false)
const mouseX = ref(0)
const mouseY = ref(0)
const isPurpleBlinking = ref(false)
const isBlackBlinking = ref(false)
const isTyping = ref(false)
const isLookingAtEachOther = ref(false)
const isPurplePeeking = ref(false)
const isRegisterMode = ref(false)
const rememberMe = ref(false)

// Password strength
const PASSWORD_REQUIREMENTS = [
  { regex: /.{8,}/, text: '至少 8 个字符' },
  { regex: /[0-9]/, text: '至少 1 个数字' },
  { regex: /[a-z]/, text: '至少 1 个小写字母' },
  { regex: /[A-Z]/, text: '至少 1 个大写字母' },
  { regex: /[!-/:-@[-`{-~]/, text: '至少 1 个特殊字符' },
]

const STRENGTH_COLORS = ['bg-white/10', 'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-amber-700', 'bg-emerald-500']
const STRENGTH_TEXTS = ['请输入密码', '弱密码', '中等密码', '强密码', '非常强密码']

const passwordStrength = computed(() => {
  const requirements = PASSWORD_REQUIREMENTS.map((req) => ({
    met: req.regex.test(password.value),
    text: req.text,
  }))
  return {
    score: requirements.filter((req) => req.met).length,
    requirements,
  }
})

const purpleRef = ref(null)
const blackRef = ref(null)
const yellowRef = ref(null)
const orangeRef = ref(null)
const particlesCanvas = ref(null)

// Particles animation
let particlesRaf = 0
let particles = []

const initParticles = () => {
  const canvas = particlesCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const setSize = () => {
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
  }
  setSize()

  const make = () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    v: Math.random() * 0.25 + 0.05,
    o: Math.random() * 0.35 + 0.15,
  })

  const init = () => {
    particles = []
    const count = Math.floor((canvas.width * canvas.height) / 9000)
    for (let i = 0; i < count; i++) particles.push(make())
  }

  const draw = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    particles.forEach((p) => {
      p.y -= p.v
      if (p.y < 0) {
        p.x = Math.random() * canvas.width
        p.y = canvas.height + Math.random() * 40
        p.v = Math.random() * 0.25 + 0.05
        p.o = Math.random() * 0.35 + 0.15
      }
      ctx.fillStyle = `rgba(250,250,250,${p.o})`
      ctx.fillRect(p.x, p.y, 0.7, 2.2)
    })
    particlesRaf = requestAnimationFrame(draw)
  }

  const onResize = () => { setSize(); init() }
  window.addEventListener('resize', onResize)
  init()
  particlesRaf = requestAnimationFrame(draw)

  return () => {
    window.removeEventListener('resize', onResize)
    cancelAnimationFrame(particlesRaf)
  }
}

const handleMouseMove = (e) => {
  mouseX.value = e.clientX
  mouseY.value = e.clientY
}

let purpleBlinkTimeout = null
let blackBlinkTimeout = null

const schedulePurpleBlink = () => {
  const interval = Math.random() * 4000 + 3000
  purpleBlinkTimeout = setTimeout(() => {
    isPurpleBlinking.value = true
    setTimeout(() => {
      isPurpleBlinking.value = false
      schedulePurpleBlink()
    }, 150)
  }, interval)
}

const scheduleBlackBlink = () => {
  const interval = Math.random() * 4000 + 3000
  blackBlinkTimeout = setTimeout(() => {
    isBlackBlinking.value = true
    setTimeout(() => {
      isBlackBlinking.value = false
      scheduleBlackBlink()
    }, 150)
  }, interval)
}

let typingTimer = null

const handleInputFocus = () => { isTyping.value = true }
const handleInputBlur = () => {
  if (typingTimer) clearTimeout(typingTimer)
  typingTimer = setTimeout(() => { isTyping.value = false }, 800)
}

let peekTimeout = null

watch([() => password.value, showPassword, isPurplePeeking], () => {
  if (password.value.length > 0 && showPassword.value) {
    if (peekTimeout) clearTimeout(peekTimeout)
    peekTimeout = setTimeout(() => {
      isPurplePeeking.value = true
      setTimeout(() => { isPurplePeeking.value = false }, 800)
    }, Math.random() * 3000 + 2000)
  } else {
    isPurplePeeking.value = false
  }
})

watch(isTyping, (val) => {
  if (val) {
    isLookingAtEachOther.value = true
    const timer = setTimeout(() => { isLookingAtEachOther.value = false }, 800)
    return () => clearTimeout(timer)
  } else {
    isLookingAtEachOther.value = false
  }
})

const calculatePosition = (el) => {
  if (!el) return { faceX: 0, faceY: 0, bodySkew: 0 }
  const rect = el.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 3
  const deltaX = mouseX.value - centerX
  const deltaY = mouseY.value - centerY
  const faceX = Math.max(-15, Math.min(15, deltaX / 20))
  const faceY = Math.max(-10, Math.min(10, deltaY / 30))
  const bodySkew = Math.max(-6, Math.min(6, -deltaX / 120))
  return { faceX, faceY, bodySkew }
}

const purplePos = computed(() => calculatePosition(purpleRef.value))
const blackPos = computed(() => calculatePosition(blackRef.value))
const yellowPos = computed(() => calculatePosition(yellowRef.value))
const orangePos = computed(() => calculatePosition(orangeRef.value))

const calculatePupilPosition = (el, maxDistance, forceX, forceY) => {
  if (forceX !== undefined && forceY !== undefined) return { x: forceX, y: forceY }
  if (!el) return { x: 0, y: 0 }
  const rect = el.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const deltaX = mouseX.value - centerX
  const deltaY = mouseY.value - centerY
  const distance = Math.min(Math.sqrt(deltaX ** 2 + deltaY ** 2), maxDistance)
  const angle = Math.atan2(deltaY, deltaX)
  return { x: Math.cos(angle) * distance, y: Math.sin(angle) * distance }
}

const isPasswordVisible = computed(() => password.value.length > 0 && showPassword.value)
const isPasswordHidden = computed(() => password.value.length > 0 && !showPassword.value)
const isPasswordActive = computed(() => isTyping.value || isPasswordHidden.value)

const purpleStyle = computed(() => {
  const skew = isPasswordVisible.value ? 0 : isPasswordActive.value ? (purplePos.value.bodySkew || 0) - 12 : (purplePos.value.bodySkew || 0)
  const translateX = isPasswordActive.value && !isPasswordVisible.value ? 40 : 0
  return { transform: `skewX(${skew}deg) translateX(${translateX}px)`, transformOrigin: 'bottom center', height: isPasswordActive.value ? '440px' : '400px' }
})

const purpleEyesStyle = computed(() => ({
  left: isPasswordVisible.value ? '20px' : isLookingAtEachOther.value ? '55px' : `${45 + purplePos.value.faceX}px`,
  top: isPasswordVisible.value ? '35px' : isLookingAtEachOther.value ? '65px' : `${40 + purplePos.value.faceY}px`,
}))

const purpleEyeForceLook = computed(() => {
  if (isPasswordVisible.value) return { x: isPurplePeeking.value ? 4 : -4, y: isPurplePeeking.value ? 5 : -4 }
  if (isLookingAtEachOther.value) return { x: 3, y: 4 }
  return { x: undefined, y: undefined }
})

const blackStyle = computed(() => {
  let skew
  if (isPasswordVisible.value) skew = 0
  else if (isLookingAtEachOther.value) skew = (blackPos.value.bodySkew || 0) * 1.5 + 10
  else if (isPasswordActive.value) skew = (blackPos.value.bodySkew || 0) * 1.5
  else skew = blackPos.value.bodySkew || 0
  return { transform: `skewX(${skew}deg) translateX(${isLookingAtEachOther.value ? 20 : 0}px)`, transformOrigin: 'bottom center' }
})

const blackEyesStyle = computed(() => ({
  left: isPasswordVisible.value ? '10px' : isLookingAtEachOther.value ? '32px' : `${26 + blackPos.value.faceX}px`,
  top: isPasswordVisible.value ? '28px' : isLookingAtEachOther.value ? '12px' : `${32 + blackPos.value.faceY}px`,
}))

const blackEyeForceLook = computed(() => {
  if (isPasswordVisible.value) return { x: -4, y: -4 }
  if (isLookingAtEachOther.value) return { x: 0, y: -4 }
  return { x: undefined, y: undefined }
})

const orangeStyle = computed(() => ({ transform: `skewX(${isPasswordVisible.value ? 0 : (orangePos.value.bodySkew || 0)}deg)`, transformOrigin: 'bottom center' }))
const orangeEyesStyle = computed(() => ({ left: isPasswordVisible.value ? '50px' : `${82 + (orangePos.value.faceX || 0)}px`, top: isPasswordVisible.value ? '85px' : `${90 + (orangePos.value.faceY || 0)}px` }))
const orangePupilForceLook = computed(() => isPasswordVisible.value ? { x: -5, y: -4 } : { x: undefined, y: undefined })

const yellowStyle = computed(() => ({ transform: `skewX(${isPasswordVisible.value ? 0 : (yellowPos.value.bodySkew || 0)}deg)`, transformOrigin: 'bottom center' }))
const yellowEyesStyle = computed(() => ({ left: isPasswordVisible.value ? '20px' : `${52 + (yellowPos.value.faceX || 0)}px`, top: isPasswordVisible.value ? '35px' : `${40 + (yellowPos.value.faceY || 0)}px` }))
const yellowMouthStyle = computed(() => ({ left: isPasswordVisible.value ? '10px' : `${40 + (yellowPos.value.faceX || 0)}px`, top: isPasswordVisible.value ? '88px' : `${88 + (yellowPos.value.faceY || 0)}px` }))
const yellowPupilForceLook = computed(() => isPasswordVisible.value ? { x: -5, y: -4 } : { x: undefined, y: undefined })

const handleSubmit = async (e) => {
  e.preventDefault()
  error.value = ''
  isLoading.value = true
  try {
    if (isRegisterMode.value) {
      if (!username.value || !email.value || !password.value || !confirmPassword.value) { error.value = '请填写所有字段'; return }
      if (password.value !== confirmPassword.value) { error.value = '两次输入的密码不一致'; return }
      if (password.value.length < 6) { error.value = '密码长度至少6位'; return }
      await authStore.register(username.value, email.value, password.value)
      router.push('/profile-onboarding')
    } else {
      if (!email.value || !password.value) { error.value = '请输入邮箱和密码'; return }
      await authStore.login(email.value, password.value)
      router.push('/dashboard')
    }
  } catch (err) {
    error.value = err.error || (isRegisterMode.value ? '注册失败，请重试' : '登录失败，请检查邮箱和密码')
  } finally { isLoading.value = false }
}

const syncModeWithRoute = () => {
  isRegisterMode.value = route.path === '/register'
}

const toggleMode = async () => {
  error.value = ''
  if (isRegisterMode.value) {
    await router.push('/login')
  } else {
    await router.push('/register')
  }
}

watch(() => route.path, () => {
  syncModeWithRoute()
})

onMounted(() => {
  syncModeWithRoute()
  window.addEventListener('mousemove', handleMouseMove)
  schedulePurpleBlink()
  scheduleBlackBlink()
  initParticles()
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  if (purpleBlinkTimeout) clearTimeout(purpleBlinkTimeout)
  if (blackBlinkTimeout) clearTimeout(blackBlinkTimeout)
  if (typingTimer) clearTimeout(typingTimer)
  if (peekTimeout) clearTimeout(peekTimeout)
  cancelAnimationFrame(particlesRaf)
})
</script>

<template>
  <div class="min-h-screen grid lg:grid-cols-2">
    <!-- Left Content Section -->
    <div class="relative hidden lg:flex flex-col justify-between bg-gradient-to-br from-[#DDDDDD]/90 via-[#DDDDDD] to-[#DDDDDD]/80 p-12 text-gray-800">
      <div class="relative z-20">
        <div class="flex items-center gap-2 text-lg font-semibold">
          
        </div>
      </div>

      <div class="relative z-20 flex items-end justify-center" style="height: 500px;">
        <div class="relative" style="width: 550px; height: 400px;">
          <!-- Purple character -->
          <div ref="purpleRef" class="absolute bottom-0 transition-all duration-700 ease-in-out" :style="{ left: '70px', width: '180px', backgroundColor: '#4B5563', borderRadius: '10px 10px 0 0', zIndex: 1, ...purpleStyle }">
            <div class="absolute flex gap-8 transition-all duration-700 ease-in-out" :style="purpleEyesStyle">
              <div class="rounded-full flex items-center justify-center transition-all duration-150" :style="{ width: '18px', height: isPurpleBlinking ? '2px' : '18px', backgroundColor: 'white', overflow: 'hidden' }">
                <div v-if="!isPurpleBlinking" class="rounded-full" :style="{ width: '7px', height: '7px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(purpleRef, 5, purpleEyeForceLook.x, purpleEyeForceLook.y).x}px, ${calculatePupilPosition(purpleRef, 5, purpleEyeForceLook.x, purpleEyeForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
              </div>
              <div class="rounded-full flex items-center justify-center transition-all duration-150" :style="{ width: '18px', height: isPurpleBlinking ? '2px' : '18px', backgroundColor: 'white', overflow: 'hidden' }">
                <div v-if="!isPurpleBlinking" class="rounded-full" :style="{ width: '7px', height: '7px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(purpleRef, 5, purpleEyeForceLook.x, purpleEyeForceLook.y).x}px, ${calculatePupilPosition(purpleRef, 5, purpleEyeForceLook.x, purpleEyeForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
              </div>
            </div>
          </div>

          <!-- Black character -->
          <div ref="blackRef" class="absolute bottom-0 transition-all duration-700 ease-in-out" :style="{ left: '240px', width: '120px', height: '310px', backgroundColor: '#2D2D2D', borderRadius: '8px 8px 0 0', zIndex: 2, ...blackStyle }">
            <div class="absolute flex gap-6 transition-all duration-700 ease-in-out" :style="blackEyesStyle">
              <div class="rounded-full flex items-center justify-center transition-all duration-150" :style="{ width: '16px', height: isBlackBlinking ? '2px' : '16px', backgroundColor: 'white', overflow: 'hidden' }">
                <div v-if="!isBlackBlinking" class="rounded-full" :style="{ width: '6px', height: '6px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(blackRef, 4, blackEyeForceLook.x, blackEyeForceLook.y).x}px, ${calculatePupilPosition(blackRef, 4, blackEyeForceLook.x, blackEyeForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
              </div>
              <div class="rounded-full flex items-center justify-center transition-all duration-150" :style="{ width: '16px', height: isBlackBlinking ? '2px' : '16px', backgroundColor: 'white', overflow: 'hidden' }">
                <div v-if="!isBlackBlinking" class="rounded-full" :style="{ width: '6px', height: '6px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(blackRef, 4, blackEyeForceLook.x, blackEyeForceLook.y).x}px, ${calculatePupilPosition(blackRef, 4, blackEyeForceLook.x, blackEyeForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
              </div>
            </div>
          </div>

          <!-- Orange semi-circle character -->
          <div ref="orangeRef" class="absolute bottom-0 transition-all duration-700 ease-in-out" :style="{ left: '0px', width: '240px', height: '200px', zIndex: 3, backgroundColor: '#FF9B6B', borderRadius: '120px 120px 0 0', ...orangeStyle }">
            <div class="absolute flex gap-8 transition-all duration-200 ease-out" :style="orangeEyesStyle">
              <div class="rounded-full" :style="{ width: '12px', height: '12px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(orangeRef, 5, orangePupilForceLook.x, orangePupilForceLook.y).x}px, ${calculatePupilPosition(orangeRef, 5, orangePupilForceLook.x, orangePupilForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
              <div class="rounded-full" :style="{ width: '12px', height: '12px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(orangeRef, 5, orangePupilForceLook.x, orangePupilForceLook.y).x}px, ${calculatePupilPosition(orangeRef, 5, orangePupilForceLook.x, orangePupilForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
            </div>
          </div>

          <!-- Yellow character -->
          <div ref="yellowRef" class="absolute bottom-0 transition-all duration-700 ease-in-out" :style="{ left: '310px', width: '140px', height: '230px', backgroundColor: '#E8D754', borderRadius: '70px 70px 0 0', zIndex: 4, ...yellowStyle }">
            <div class="absolute flex gap-6 transition-all duration-200 ease-out" :style="yellowEyesStyle">
              <div class="rounded-full" :style="{ width: '12px', height: '12px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(yellowRef, 5, yellowPupilForceLook.x, yellowPupilForceLook.y).x}px, ${calculatePupilPosition(yellowRef, 5, yellowPupilForceLook.x, yellowPupilForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
              <div class="rounded-full" :style="{ width: '12px', height: '12px', backgroundColor: '#2D2D2D', transform: `translate(${calculatePupilPosition(yellowRef, 5, yellowPupilForceLook.x, yellowPupilForceLook.y).x}px, ${calculatePupilPosition(yellowRef, 5, yellowPupilForceLook.x, yellowPupilForceLook.y).y}px)`, transition: 'transform 0.1s ease-out' }" />
            </div>
            <div class="absolute rounded-full transition-all duration-200 ease-out" :style="{ width: '80px', height: '4px', backgroundColor: '#2D2D2D', ...yellowMouthStyle }" />
          </div>
        </div>
      </div>

      <div class="relative z-20 flex items-center gap-8 text-sm text-white/60">
        
      </div>

      <div class="absolute inset-0 bg-grid-white/[0.05]" style="background-size: 20px 20px;" />
      <div class="absolute top-1/4 right-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
      <div class="absolute bottom-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
    </div>

    <!-- Right Login Section -->
    <div class="relative flex items-center justify-center bg-zinc-950 text-zinc-50 overflow-hidden">
      <!-- Subtle vignette -->
      <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(120% 80% at 50% 100%, rgba(255,255,255,0.08), transparent 70%)" />

      <!-- Animated accent lines -->
      <div class="accent-lines">
        <div class="hline" />
        <div class="hline" />
        <div class="hline" />
        <div class="vline" />
        <div class="vline" />
        <div class="vline" />
      </div>

      <!-- Particles canvas -->
      <canvas ref="particlesCanvas" class="absolute inset-0 w-full h-full opacity-50 mix-blend-screen pointer-events-none" />

      <!-- Centered Login Block -->
      <div class="relative z-10 h-full w-full flex items-center justify-center px-4 sm:px-6">
        <div class="w-full max-w-md flex flex-col items-center justify-center gap-5">
          <div class="card-animate w-full">
          <!-- Card Header -->
          <div class="flex flex-col space-y-2 p-5">
            <h1 class="text-2xl font-bold tracking-tight text-white">{{ isRegisterMode ? '创建账号' : '欢迎回来' }}</h1>
            <p class="text-sm text-zinc-500"><br></p>
          </div>

          <!-- Card Content -->
          <form @submit="handleSubmit" class="p-5 pt-0 grid gap-4">
            <!-- Username (register only) -->
            <div v-if="isRegisterMode" class="grid gap-2">
              <label for="username" class="text-sm font-medium text-zinc-400">用户名</label>
              <div class="relative">
                <input v-model="username" id="username" type="text" placeholder="请输入用户名" autocomplete="off" required class="flex h-10 w-full rounded-lg border border-zinc-300 bg-[#ffffff] pl-8 pr-10 py-2 text-sm text-zinc-900 shadow-sm transition-shadow placeholder:text-zinc-400 focus-visible:border-zinc-500 focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-zinc-500/20" @focus="handleInputFocus" @blur="handleInputBlur" />
                <User class="absolute right-3 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-zinc-400" />
              </div>
            </div>

            <!-- Email -->
            <div class="grid gap-2">
              <label for="email" class="text-sm font-medium text-zinc-400">{{ isRegisterMode ? '邮箱' : '邮箱 / 用户名' }}</label>
              <div class="relative">
                <input v-model="email" id="email" type="text" :placeholder="isRegisterMode ? 'you@example.com' : '请输入邮箱或用户名'" autocomplete="off" required class="flex h-10 w-full rounded-lg border border-zinc-300 bg-[#ffffff] pl-8 pr-10 py-2 text-sm text-zinc-900 shadow-sm transition-shadow placeholder:text-zinc-400 focus-visible:border-zinc-500 focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-zinc-500/20" @focus="handleInputFocus" @blur="handleInputBlur" />
                <Mail class="absolute right-3 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-zinc-400" />
              </div>
            </div>

            <!-- Password -->
            <div class="grid gap-2">
              <label for="password" class="text-sm font-medium text-zinc-400">密码</label>
              <div class="relative">
                <input v-model="password" id="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required class="flex h-10 w-full rounded-lg border border-zinc-300 bg-[#ffffff] pl-8 pr-10 py-2 text-sm text-zinc-900 shadow-sm transition-shadow placeholder:text-zinc-400 focus-visible:border-zinc-500 focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-zinc-500/20" @focus="handleInputFocus" @blur="handleInputBlur" />
                <button type="button" @click="showPassword = !showPassword" class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-md text-zinc-400 hover:text-zinc-600 transition-colors">
                  <EyeOff v-if="showPassword" class="h-[18px] w-[18px]" />
                  <Eye v-else class="h-[18px] w-[18px]" />
                </button>
              </div>

            </div>

            <!-- Confirm Password (register only) -->
            <div v-if="isRegisterMode" class="grid gap-2">
              <label for="confirmPassword" class="text-sm font-medium text-zinc-400">确认密码</label>
              <div class="relative">
                <input v-model="confirmPassword" id="confirmPassword" :type="showPassword ? 'text' : 'password'" placeholder="请再次输入密码" required class="flex h-10 w-full rounded-lg border border-zinc-300 bg-[#ffffff] pl-8 pr-10 py-2 text-sm text-zinc-900 shadow-sm transition-shadow placeholder:text-zinc-400 focus-visible:border-zinc-500 focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-zinc-500/20" @focus="handleInputFocus" @blur="handleInputBlur" />
              </div>
            </div>

            <!-- Remember me / Forgot password (login only) -->
            <div v-if="!isRegisterMode" class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <input v-model="rememberMe" type="checkbox" id="remember" class="h-4 w-4 shrink-0 rounded-sm border border-zinc-700 bg-zinc-950 accent-zinc-50" />
                <label for="remember" class="text-sm text-zinc-400 cursor-pointer">记住我</label>
              </div>
              <a href="#" class="text-sm text-zinc-300 hover:text-zinc-100 transition-colors">忘记密码？</a>
            </div>

            <!-- Error -->
            <div v-if="error" class="p-3 text-sm text-red-400 bg-red-950/20 border border-red-900/30 rounded-lg">{{ error }}</div>

            <!-- Submit -->
            <br>
            <button type="submit" :disabled="isLoading" class="inline-flex items-center justify-center w-full h-10 rounded-lg bg-zinc-50 text-zinc-900 text-sm font-semibold hover:bg-zinc-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              <span v-if="isLoading" class="w-4 h-4 border-2 border-zinc-900/30 border-t-zinc-900 rounded-full animate-spin mr-2"></span>
              {{ isLoading ? '处理中...' : (isRegisterMode ? '注册' : '继续') }}
            </button>

            <!-- Separator -->
            <div class="relative">
              <div class="shrink-0 h-[1px] w-full bg-zinc-800" />
              <span class="absolute left-1/2 -translate-x-1/2 -top-3 bg-zinc-900/70 px-2 text-[11px] uppercase tracking-widest text-zinc-500">或</span>
            </div>

            <!-- Social login -->
            <div class="grid grid-cols-3 gap-3">
              <button type="button" class="inline-flex items-center justify-center h-10 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-50 text-sm font-medium hover:bg-zinc-900/80 hover:border-green-600/30 transition-colors">
                <svg class="h-[18px] w-[18px] mr-1.5" viewBox="0 0 24 24" fill="#07C160"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.534c0 2.09.955 3.99 2.52 5.38l-.633 1.912a.5.5 0 00.718.572l2.294-1.148c.82.252 1.69.396 2.593.42a5.556 5.556 0 01-.197-1.462c0-3.659 3.357-6.627 7.5-6.627.256 0 .509.013.759.036C14.848 4.896 12.081 2.188 8.691 2.188zm-2.6 4.17a1.12 1.12 0 110 2.24 1.12 1.12 0 010-2.24zm5.198 0a1.12 1.12 0 110 2.24 1.12 1.12 0 010-2.24zM14.795 9.534c-3.587 0-6.5 2.514-6.5 5.613 0 3.1 2.913 5.613 6.5 5.613.718 0 1.41-.102 2.06-.29l1.76.88a.5.5 0 00.718-.572l-.484-1.464c1.282-1.14 2.07-2.72 2.07-4.467-.2-3-3.113-5.313-6.124-5.313zm-2.28 3.456a.896.896 0 110 1.792.896.896 0 010-1.792zm4.56 0a.896.896 0 110 1.792.896.896 0 010-1.792z"/></svg>
                微信
              </button>
              <button type="button" class="inline-flex items-center justify-center h-10 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-50 text-sm font-medium hover:bg-zinc-900/80 hover:border-sky-500/30 transition-colors">
                <svg class="h-[18px] w-[18px] mr-1.5" viewBox="0 0 24 24" fill="#12B7F5"><path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7zM9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-17c-1.66 0-3 1.34-3 3h6c0-1.66-1.34-3-3-3z"/></svg>
                QQ
              </button>
              <button type="button" class="inline-flex items-center justify-center h-10 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-50 text-sm font-medium hover:bg-zinc-900/80 hover:border-blue-500/30 transition-colors">
                <svg class="h-[18px] w-[18px] mr-1.5" viewBox="0 0 24 24" fill="#3B82F6"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 2.18l7 3.12v4.7c0 4.83-3.23 9.36-7 10.58-3.77-1.22-7-5.75-7-10.58V6.3l7-3.12zm-1 5.82v2h2v-2h-2zm0 4v2h2v-2h-2z"/></svg>
                校园网
              </button>
            </div>
          </form>

          <br>
          <!-- Card Footer -->
          <div class="flex items-center justify-center px-5 pb-5 text-sm text-zinc-400">
            {{ isRegisterMode ? '已有账号？' : '还没有账号？' }}
            <button @click="toggleMode" class="ml-1 text-zinc-200 hover:underline">{{ isRegisterMode ? '立即登录' : '创建一个' }}</button>
          </div>
        </div>

          <div class="text-center">
            <button @click="$router.push('/')" class="text-sm text-zinc-600 hover:text-zinc-400 transition-colors">← 返回首页</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Accent lines */
.accent-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.7;
}

.hline,
.vline {
  position: absolute;
  background: #27272a;
  will-change: transform, opacity;
}

.hline {
  left: 0;
  right: 0;
  height: 1px;
  transform: scaleX(0);
  transform-origin: 50% 50%;
  animation: drawX 0.8s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

.vline {
  top: 0;
  bottom: 0;
  width: 1px;
  transform: scaleY(0);
  transform-origin: 50% 0%;
  animation: drawY 0.9s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

.hline:nth-child(1) { top: 18%; animation-delay: 0.12s; }
.hline:nth-child(2) { top: 50%; animation-delay: 0.22s; }
.hline:nth-child(3) { top: 82%; animation-delay: 0.32s; }
.vline:nth-child(4) { left: 22%; animation-delay: 0.42s; }
.vline:nth-child(5) { left: 50%; animation-delay: 0.54s; }
.vline:nth-child(6) { left: 78%; animation-delay: 0.66s; }

.hline::after,
.vline::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(250, 250, 250, 0.24), transparent);
  opacity: 0;
  animation: shimmer 0.9s ease-out forwards;
}

.hline:nth-child(1)::after { animation-delay: 0.12s; }
.hline:nth-child(2)::after { animation-delay: 0.22s; }
.hline:nth-child(3)::after { animation-delay: 0.32s; }
.vline:nth-child(4)::after { animation-delay: 0.42s; }
.vline:nth-child(5)::after { animation-delay: 0.54s; }
.vline:nth-child(6)::after { animation-delay: 0.66s; }

@keyframes drawX {
  0% { transform: scaleX(0); opacity: 0; }
  60% { opacity: 0.95; }
  100% { transform: scaleX(1); opacity: 0.7; }
}

@keyframes drawY {
  0% { transform: scaleY(0); opacity: 0; }
  60% { opacity: 0.95; }
  100% { transform: scaleY(1); opacity: 0.7; }
}

@keyframes shimmer {
  0% { opacity: 0; }
  35% { opacity: 0.25; }
  100% { opacity: 0; }
}

/* Card fade-up animation */
.card-animate {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeUp 0.8s cubic-bezier(0.22, 0.61, 0.36, 1) 0.4s forwards;
}

@keyframes fadeUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>