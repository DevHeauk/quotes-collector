// 반응형 레이아웃 토큰. Android Window Size Class 기준.
//   compact   < 600dp  : 일반 폰, Fold7 커버(접힘)
//   medium    600~839  : Fold7 펼침(정사각), 소형 태블릿 세로
//   expanded  >= 840    : 태블릿, Fold7 가로
export const breakpoints = {
  medium: 600,
  expanded: 840,
} as const;

export type SizeClass = 'compact' | 'medium' | 'expanded';

export function sizeClassFor(width: number): SizeClass {
  if (width >= breakpoints.expanded) {
    return 'expanded';
  }
  if (width >= breakpoints.medium) {
    return 'medium';
  }
  return 'compact';
}

// 콘텐츠 최대 폭(중앙 정렬용). compact는 사실상 제한 없음.
export const contentMaxWidth: Record<SizeClass, number> = {
  compact: 9999,
  medium: 600,
  expanded: 720,
};

// 목록(그리드) 열 수.
export const listColumns: Record<SizeClass, number> = {
  compact: 1,
  medium: 2,
  expanded: 3,
};

// 화면 가장자리 여백(gutter).
export const gutterFor: Record<SizeClass, number> = {
  compact: 16,
  medium: 24,
  expanded: 32,
};
