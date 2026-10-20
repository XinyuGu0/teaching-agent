import type { Component } from "vue"

export interface BentoItem {
  title: string
  description: string
  icon?: Component
  iconClass?: string
  status?: string
  tags?: string[]
  meta?: string
  cta?: string
  colSpan?: number
  hasPersistentHover?: boolean
}
