import { onBeforeUnmount, ref } from 'vue'

// Types a line out once, so the agent visibly speaks first rather than
// arriving pre-written. Reduced motion (or a visitor who starts typing)
// resolves the line instantly — the page must never be slower than the guest.

function reducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function useTypewriter() {
  const typed = ref('')
  const done = ref(true)
  const thinking = ref(false)
  let timer = 0
  let started = false

  function finish(text) {
    clearTimeout(timer)
    timer = 0
    thinking.value = false
    typed.value = text
    done.value = true
  }

  function reset() {
    clearTimeout(timer)
    timer = 0
    started = false
    thinking.value = false
    typed.value = ''
    done.value = true
  }

  function run(text, { speed = 12, pause = 600 } = {}) {
    if (started) return
    started = true
    if (reducedMotion()) { finish(text); return }
    done.value = false
    thinking.value = true
    timer = setTimeout(() => {
      thinking.value = false
      let i = 0
      const step = () => {
        i += 1
        typed.value = text.slice(0, i)
        if (i >= text.length) { done.value = true; timer = 0; return }
        timer = setTimeout(step, speed)
      }
      step()
    }, pause)
  }

  function skip(text) {
    if (started && !done.value) finish(text)
  }

  onBeforeUnmount(() => clearTimeout(timer))
  return { typed, done, thinking, run, skip, reset }
}
