import { ref } from 'vue'
import { ARRIVAL_KEY } from '../slogans.js'

const played =
  typeof window !== 'undefined' &&
  ((() => {
    try {
      return !!window.sessionStorage.getItem(ARRIVAL_KEY)
    } catch (e) {
      return false
    }
  })() || window.matchMedia('(prefers-reduced-motion: reduce)').matches)

export const arrived = ref(played)

export function useArrival() {
  return { arrived }
}
