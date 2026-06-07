import {useWindowDimensions} from 'react-native';
import {
  SizeClass,
  sizeClassFor,
  contentMaxWidth,
  listColumns,
  gutterFor,
} from '../constants/layout';
import {TypeScale, typeScale} from '../constants/typography';

export interface Responsive {
  width: number;
  height: number;
  sizeClass: SizeClass;
  /** 일반 폰 / Fold7 커버 */
  isCompact: boolean;
  /** Fold7 펼침(정사각) / 소형 태블릿 세로 */
  isFoldOpen: boolean;
  /** 태블릿 / Fold7 가로 */
  isTablet: boolean;
  landscape: boolean;
  /** 목록 열 수 */
  columns: number;
  /** 콘텐츠 중앙정렬 최대 폭 */
  contentMaxWidth: number;
  /** 화면 가장자리 여백 */
  gutter: number;
  /** 사이즈 클래스별 타입 스케일 */
  type: TypeScale;
}

/**
 * 반응형 레이아웃의 단일 소스.
 * useWindowDimensions 기반이라 폴드 접기/펴기·회전·멀티윈도우에 자동 반응한다.
 */
export function useResponsive(): Responsive {
  const {width, height} = useWindowDimensions();
  const sizeClass = sizeClassFor(width);
  return {
    width,
    height,
    sizeClass,
    isCompact: sizeClass === 'compact',
    isFoldOpen: sizeClass === 'medium',
    isTablet: sizeClass === 'expanded',
    landscape: width > height,
    columns: listColumns[sizeClass],
    contentMaxWidth: contentMaxWidth[sizeClass],
    gutter: gutterFor[sizeClass],
    type: typeScale[sizeClass],
  };
}
