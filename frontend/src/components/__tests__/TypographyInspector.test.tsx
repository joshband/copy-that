import { act, render, screen } from '@testing-library/react'
import TypographyInspector from '../TypographyInspector'
import { useTokenGraphStore } from '../../store/tokenGraphStore'

describe('TypographyInspector', () => {
  const initialState = useTokenGraphStore.getState()

  afterEach(() => {
    act(() => useTokenGraphStore.setState(initialState))
  })

  it('renders typography token details from graph store', () => {
    act(() =>
      useTokenGraphStore.setState((state) => ({
        ...state,
        loaded: true,
        colors: [
          {
            id: 'color.text.primary',
            category: 'color',
            raw: { $type: 'color', $value: '#111111' } as any,
            isAlias: false,
          },
        ],
        typography: [
          {
            id: 'typography.body',
            category: 'typography',
            raw: {
              $type: 'typography',
              $value: {
                fontFamily: ['{font.family.primary}'],
                fontSize: { value: 16, unit: 'px' },
                lineHeight: 1.5,
                fontWeight: 500,
                color: '{color.text.primary}',
              },
            } as any,
            referencedColorId: 'color.text.primary',
            fontFamilyTokenId: 'font.family.primary',
            fontSizeTokenId: undefined,
          },
        ],
        typographyRecommendation: {
          styleAttributes: { primary_style: 'minimalist' },
          confidence: 0.82,
        },
      })),
    )

    render(<TypographyInspector />)

    expect(screen.getByTestId('typo-specimen')).toHaveStyle({ lineHeight: '1.5' })
    expect(screen.getByText('typography.body')).toBeInTheDocument()
    expect(screen.getByText(/Font:/)).toHaveTextContent('Substituted preview')
    expect(screen.getByText(/Size:/)).toHaveTextContent('16px')
    expect(screen.getByText(/Weight:/)).toHaveTextContent('500')
    expect(screen.getByText(/Confidence/)).toHaveTextContent('82%')
  })
})
