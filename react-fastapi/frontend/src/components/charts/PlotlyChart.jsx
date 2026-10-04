import React from 'react';
import createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyConfig } from '../../utils/chartTheme';

const Plot = createPlotlyComponent(Plotly);

export function PlotlyChart({
  data = [],
  layout = {},
  config = {},
  style = {},
  className = '',
  useResizeHandler = true,
}) {
  const { isDark } = useTheme();

  const mergedConfig = {
    ...getPlotlyConfig(),
    ...config,
  };

  const defaultStyle = {
    width: '100%',
    height: '100%',
    minHeight: '340px',
    ...style,
  };

  return (
    <div
      className={`plotly-chart-wrapper ${className}`}
      style={{ width: '100%', height: '100%', minHeight: defaultStyle.minHeight, position: 'relative' }}
    >
      <Plot
        data={data}
        layout={layout}
        config={mergedConfig}
        style={defaultStyle}
        useResizeHandler={useResizeHandler}
      />
    </div>
  );
}
