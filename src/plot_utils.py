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

    xs = list(range(1, len(samples) + 1))
    mp01 = [d.get('mp01', 0) for d in samples]
    mp25 = [d.get('mp25', 0) for d in samples]
    mp10 = [d.get('mp10', 0) for d in samples]
    temp = [d.get('temp', 0) for d in samples]
    hr = [d.get('hr', 0) for d in samples]

    fig, axes = plt.subplots(6, 1, sharex=True, figsize=(8, 12))
    fig.suptitle("Mediciones - series y histograma")

    axes[0].plot(xs, mp01, '-o', color='blue')
    axes[0].set_ylabel('MP01 (ug/m3)')
    axes[0].grid(True)
    axes[0].legend(['MP01'])

    axes[1].plot(xs, mp25, '-o', color='green')
    axes[1].set_ylabel('MP25 (ug/m3)')
    axes[1].grid(True)
    axes[1].legend(['MP25'])

    axes[2].plot(xs, mp10, '-o', color='red')
    axes[2].set_ylabel('MP10 (ug/m3)')
    axes[2].grid(True)
    axes[2].legend(['MP10'])

    axes[3].plot(xs, temp, '-o', color='orange')
    axes[3].set_ylabel('Temperatura (C)')
    axes[3].grid(True)
    axes[3].legend(['Temp'])

    axes[4].plot(xs, hr, '-o', color='purple')
    axes[4].set_ylabel('Humedad (%)')
    axes[4].grid(True)
    axes[4].legend(['HR'])

    # Histogram placeholder - compute last values histogram
    try:
        h_vals = [samples[-1].get('h01', 0), samples[-1].get('h25', 0), samples[-1].get('h50', 0), samples[-1].get('h10', 0)]
    except Exception:
        h_vals = [0, 0, 0, 0]

    axes[5].bar(['h01','h25','h50','h10'], h_vals, color=['green','yellow','red','blue'])
    axes[5].set_ylabel('Histogram')
    axes[5].grid(True)

    axes[-1].set_xlabel('Samples')

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
    labels = ['h01','h25','h50','h10']
    vals = [values_dict.get(k, 0) for k in labels]
    ax.bar(labels, vals, color=['green','yellow','red','blue'])
    ax.set_title('Histograma')
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf
