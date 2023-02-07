import { compose, list_compose, proper_subsets } from './utils'

test('proper_subsets', () => {
  expect(proper_subsets([1, 2])).toStrictEqual([[1], [2], [1, 2]])
})

test('compose', () => {
  expect(
    compose(
      [
        [1, 2],
        [3, 4],
      ],
      [5, 6]
    )
  ).toStrictEqual([
    [1, 2, 5],
    [1, 2, 6],
    [3, 4, 5],
    [3, 4, 6],
  ])
})

test('list_compose', () => {
  expect(
    list_compose([
      [1, 2],
      [3, 4],
    ])
  ).toStrictEqual([
    [1, 3],
    [1, 4],
    [2, 3],
    [2, 4],
  ])
})
