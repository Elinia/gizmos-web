export function shuffle<T>(arr: T[]) {
  return [...arr].sort(() => 0.5 - Math.random())
}

export function random_int(max: number) {
  return Math.floor(Math.random() * max)
}

export function proper_subsets<T>(arr: T[]) {
  let subsets: T[][] = [[]]
  arr.forEach(v => {
    const new_subsets = subsets.map(subset => [...subset, v])
    subsets = [...subsets, ...new_subsets]
  })
  return subsets.filter(subset => subset.length > 0)
}

export function sample<T>(arr: T[]) {
  return arr[random_int(arr.length)]
}

export function compose<T>(a: T[][], b: T[]) {
  const res: T[][] = []
  a.forEach(_a => b.forEach(_b => res.push([..._a, _b])))
  return res
}

export function list_compose<T>(list: T[][]) {
  return list.reduce((acc, curr) => compose(acc, curr), [[]] as T[][])
}
