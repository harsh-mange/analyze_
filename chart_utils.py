import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Optional
import numpy as np

class ChartCreator:
    """Class for creating interactive charts using Plotly."""
    
    @staticmethod
    def create_candlestick_chart(df: pd.DataFrame, symbol: str, 
                                show_indicators: bool = True) -> go.Figure:
        """Create an interactive candlestick chart with technical indicators."""
        
        # Create subplots for price and volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} - Price Chart', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='OHLC',
                increasing_line_color='#26A69A',
                decreasing_line_color='#EF5350'
            ),
            row=1, col=1
        )
        
        # Add technical indicators if available and requested
        if show_indicators:
            # SMA20
            if 'SMA20' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA20'],
                        mode='lines',
                        name='SMA20',
                        line=dict(color='#FF9800', width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            # SMA50
            if 'SMA50' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA50'],
                        mode='lines',
                        name='SMA50',
                        line=dict(color='#2196F3', width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            # Bollinger Bands
            if all(col in df.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
                # Upper band
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['BB_Upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='rgba(255, 193, 7, 0.5)', width=1),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                # Middle band
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['BB_Middle'],
                        mode='lines',
                        name='BB Middle',
                        line=dict(color='rgba(255, 193, 7, 0.3)', width=1),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                # Lower band
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='rgba(255, 193, 7, 0.5)', width=1),
                        fill='tonexty',
                        fillcolor='rgba(255, 193, 7, 0.1)',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # Volume chart
        colors = ['#26A69A' if close >= open else '#EF5350' 
                 for close, open in zip(df['close'], df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Technical Analysis Chart',
            xaxis_rangeslider_visible=False,
            height=700,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_technical_indicators_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
        """Create a separate chart for technical indicators."""
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('RSI', 'MACD', 'Volume Analysis'),
            row_width=[0.33, 0.33, 0.34]
        )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='#9C27B0', width=2)
                ),
                row=1, col=1
            )
            
            # Add RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="Overbought (70)", row=1, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         annotation_text="Oversold (30)", row=1, col=1)
            fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                         annotation_text="Neutral (50)", row=1, col=1)
        
        # MACD
        if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='#2196F3', width=2)
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD_Signal'],
                    mode='lines',
                    name='MACD Signal',
                    line=dict(color='#FF9800', width=2)
                ),
                row=2, col=1
            )
            
            # MACD Histogram
            colors = ['#26A69A' if val >= 0 else '#EF5350' 
                     for val in df['MACD_Histogram']]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['MACD_Histogram'],
                    name='MACD Histogram',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # Volume Analysis
        if 'Volume_Ratio' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Volume_Ratio'],
                    mode='lines',
                    name='Volume Ratio',
                    line=dict(color='#4CAF50', width=2)
                ),
                row=3, col=1
            )
            
            # Add volume ratio reference line
            fig.add_hline(y=1, line_dash="dash", line_color="gray", 
                         annotation_text="Average Volume (1.0)", row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Technical Indicators',
            height=800,
            template='plotly_white',
            hovermode='x unified',
            showlegend=True
        )
        
        # Update axes
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="RSI", row=1, col=1)
        fig.update_yaxes(title_text="MACD", row=2, col=1)
        fig.update_yaxes(title_text="Volume Ratio", row=3, col=1)
        
        return fig
    
    @staticmethod
    def create_price_summary_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
        """Create a summary chart showing price statistics."""
        
        # Calculate price statistics
        latest_close = df['close'].iloc[-1]
        latest_open = df['open'].iloc[-1]
        latest_high = df['high'].iloc[-1]
        latest_low = df['low'].iloc[-1]
        
        # Calculate daily change
        if len(df) > 1:
            prev_close = df['close'].iloc[-2]
            daily_change = latest_close - prev_close
            daily_change_pct = (daily_change / prev_close) * 100
        else:
            daily_change = 0
            daily_change_pct = 0
        
        # Create gauge chart for daily change
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=latest_close,
            delta={'reference': prev_close if len(df) > 1 else latest_close},
            gauge={
                'axis': {'range': [None, latest_high * 1.1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, latest_low], 'color': "lightgray"},
                    {'range': [latest_low, latest_close], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': latest_high
                }
            },
            title={'text': f"{symbol} - Current Price"}
        ))
        
        fig.update_layout(
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_prediction_chart(df: pd.DataFrame, prediction_data: Dict, symbol: str) -> go.Figure:
        """Create a chart showing the prediction analysis."""
        
        if not prediction_data or 'prediction' not in prediction_data:
            return go.Figure()
        
        # Get the last few data points for trend visualization
        recent_data = df.tail(30)
        
        fig = go.Figure()
        
        # Historical close prices
        fig.add_trace(
            go.Scatter(
                x=recent_data.index,
                y=recent_data['close'],
                mode='lines+markers',
                name='Historical Close',
                line=dict(color='#2196F3', width=2)
            )
        )
        
        # Add prediction point
        if isinstance(prediction_data['prediction'], (int, float)):
            # Add one more day for prediction
            last_date = recent_data.index[-1]
            next_date = last_date + pd.Timedelta(days=1)
            
            fig.add_trace(
                go.Scatter(
                    x=[next_date],
                    y=[prediction_data['prediction']],
                    mode='markers',
                    name='Prediction',
                    marker=dict(
                        color='red',
                        size=12,
                        symbol='diamond'
                    )
                )
            )
            
            # Add trend line
            if len(recent_data) >= 2:
                x_trend = [recent_data.index[-1], next_date]
                y_trend = [recent_data['close'].iloc[-1], prediction_data['prediction']]
                
                fig.add_trace(
                    go.Scatter(
                        x=x_trend,
                        y=y_trend,
                        mode='lines',
                        name='Trend',
                        line=dict(color='red', width=2, dash='dash')
                    )
                )
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Price Prediction Analysis',
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            height=500,
            template='plotly_white',
            showlegend=True
        )
        
        return fig 