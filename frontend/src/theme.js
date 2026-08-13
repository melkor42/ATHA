// Persona-tinted pulse palettes for the Theater network (Phase B).
// Each ColorToken maps to a family of shades harmonizing with its
// accent token in style.css (--primary, --accent-tok, --success, --warning).
export const ACCENT_HUES = {
  // cool blue family (--primary #5E92C4)
  primary: ['#6FA8DC', '#8FC4EE', '#5E92C4', '#9DBDF7', '#74D2E4'],
  // mauve family (--accent-tok #BD8794)
  accent: ['#BD8794', '#D8A8B4', '#A6707E', '#C9A3D6', '#E5C0CA'],
  // green-teal moss family (--success #8FA96E)
  success: ['#8FA96E', '#A9C688', '#79BF9F', '#9AD8C0', '#B8D98F'],
  // ember/amber family (--warning #D8A24C)
  warning: ['#D8A24C', '#E8BC6E', '#D08840', '#F0D08E', '#E2784E']
}

// fallback: the original turquoise signal field
export const DEFAULT_HUES = ['#5FD9CB', '#6FC7F2', '#8FE8DC', '#9DBDF7', '#4FE3C1']
