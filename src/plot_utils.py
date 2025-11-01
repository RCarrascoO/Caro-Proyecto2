from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def build_timeseries_plot(samples):
    """
    samples: list of dicts with keys: 'mp01','mp25','mp10','temp','hr'
    Returns: BytesIO with PNG image
    """
    if not samples:
        raise ValueError("No samples provided")

    # x-axis: sample index (or could be timestamps if provided)
    xs = list(range(1, len(samples) + 1))
    mp01 = [d.get('mp01', 0) for d in samples]
    mp25 = [d.get('mp25', 0) for d in samples]
    mp10 = [d.get('mp10', 0) for d in samples]
    temp = [d.get('temp', 0) for d in samples]
    hr = [d.get('hr', 0) for d in samples]


from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def moving_average(data, window=10):
    if window <= 0:
        return data
    ma = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        window_vals = data[start:i + 1]
        ma.append(sum(window_vals) / len(window_vals))
    return ma


def build_timeseries_plot(samples, title: str = None):
    """
    Build a 6-row figure matching the project spec:
      1) Temperature (te) - row 1
      2) Humidity (hr) - row 2
      3) MP01 timeseries - row 3
      4) MP25 timeseries - row 4
      5) MP10 timeseries - row 5
      6) Histogram of h01,h25,h50,h10 - row 6

    samples: list of dicts. Each dict may contain 'ts' (unix), and fields: te, hr, mp01, mp25, mp10, h01, h25, h50, h10
    Returns BytesIO PNG.
    """
    if not samples:
        raise ValueError("No samples provided")

    # x values: use timestamps if present, otherwise sample index
    use_ts = False
    if all(isinstance(s.get('ts'), (int, float)) for s in samples):
        xs = [s.get('ts') for s in samples]
        use_ts = True
    else:
        xs = list(range(1, len(samples) + 1))

    # extract series in the order specified by PDF
    temp = [s.get('te', 0) for s in samples]
    hr = [s.get('hr', 0) for s in samples]
    mp01 = [s.get('mp01', 0) for s in samples]
    mp25 = [s.get('mp25', 0) for s in samples]
    mp10 = [s.get('mp10', 0) for s in samples]

    # histogram values come from the most recent sample
    last = samples[-1]
    h_vals = [last.get('h01', 0), last.get('h25', 0), last.get('h50', 0), last.get('h10', 0)]

    fig, axes = plt.subplots(6, 1, sharex=True, figsize=(9, 13))
    if title:
        fig.suptitle(title, fontsize=14)
    else:
        fig.suptitle('Mediciones - series y histograma', fontsize=14)

    # Row 1: Temperature
    axes[0].plot(xs, temp, marker='s', color='#d62728', markersize=4, linewidth=1)
    axes[0].plot(xs, moving_average(temp, window=10), color='#8c1d1d', linewidth=1)
    axes[0].set_ylabel('Temp (°C)')
    axes[0].grid(True)
    axes[0].legend(['Temp', 'MA(10)'], fontsize=8)

    # Row 2: Humidity
    axes[1].plot(xs, hr, marker='s', color='#1f77b4', markersize=4, linewidth=1)
    axes[1].plot(xs, moving_average(hr, window=10), color='#143d6b', linewidth=1)
    axes[1].set_ylabel('Humedad (%)')
    axes[1].grid(True)
    axes[1].legend(['HR', 'MA(10)'], fontsize=8)

    # Row 3: MP01
    axes[2].plot(xs, mp01, marker='s', color='#2ca02c', markersize=4, linewidth=1)
    axes[2].plot(xs, moving_average(mp01, window=10), color='#166916', linewidth=1)
    axes[2].set_ylabel('MP01 (µg/m³)')
    axes[2].grid(True)
    axes[2].legend(['MP01', 'MA(10)'], fontsize=8)

    # Row 4: MP25
    axes[3].plot(xs, mp25, marker='s', color='#ff7f0e', markersize=4, linewidth=1)
    axes[3].plot(xs, moving_average(mp25, window=10), color='#b25600', linewidth=1)
    axes[3].set_ylabel('MP25 (µg/m³)')
    axes[3].grid(True)
    axes[3].legend(['MP25', 'MA(10)'], fontsize=8)

    # Row 5: MP10
    axes[4].plot(xs, mp10, marker='s', color='#9467bd', markersize=4, linewidth=1)
    axes[4].plot(xs, moving_average(mp10, window=10), color='#4b2b6f', linewidth=1)
    axes[4].set_ylabel('MP10 (µg/m³)')
    axes[4].grid(True)
    axes[4].legend(['MP10', 'MA(10)'], fontsize=8)

    # Row 6: Histogram of last sample
    axes[5].bar(['h01', 'h25', 'h50', 'h10'], h_vals, color=['#2ca02c', '#ffeb3b', '#f03b20', '#1f77b4'])
    axes[5].set_ylabel('Histograma')
    axes[5].set_ylim(bottom=0)
    axes[5].grid(True)

    # X-axis formatting
    if use_ts:
        try:
            import datetime
            ticks = xs
            labels = [datetime.datetime.fromtimestamp(int(t)).strftime('%H:%M:%S') for t in ticks]
            axes[-1].set_xticks(xs)
            axes[-1].set_xticklabels(labels, rotation=30, fontsize=8)
        except Exception:
            axes[-1].set_xlabel('Samples')
    else:
        axes[-1].set_xlabel('Samples')
        axes[-1].set_xticks(xs)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def build_histogram_from_values(values_dict):
    """
    values_dict: dict with keys 'h01','h25','h50','h10'
    Returns: BytesIO PNG
    """
    fig, ax = plt.subplots(figsize=(6, 2))
    labels = ['h01', 'h25', 'h50', 'h10']
    vals = [values_dict.get(k, 0) for k in labels]
    ax.bar(labels, vals, color=['#2ca02c', '#ffeb3b', '#f03b20', '#1f77b4'])
    ax.set_title('Histograma')
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf
