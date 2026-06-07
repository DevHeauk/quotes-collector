import {SizeClass} from './layout';

// 사이즈 클래스별 타입 스케일. 넓은 화면에서 살짝 키워 가독성 확보.
export interface TypeScale {
  h1: number; // 화면 제목
  h2: number; // 섹션 제목
  title: number; // 카드 제목
  body: number; // 본문
  caption: number; // 보조 텍스트
  quote: number; // 명언 본문(강조)
}

export const typeScale: Record<SizeClass, TypeScale> = {
  compact: {h1: 28, h2: 22, title: 18, body: 16, caption: 13, quote: 24},
  medium: {h1: 30, h2: 24, title: 19, body: 17, caption: 13, quote: 26},
  expanded: {h1: 34, h2: 26, title: 20, body: 18, caption: 14, quote: 28},
};
