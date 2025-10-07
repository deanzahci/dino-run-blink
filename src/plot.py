from matplotlib import pyplot as plt

from config import MAX_DISPLAY_TIME


def plot_data(
    ax,
    fig,
    deque_time,
    deque_rms_combined,
    deque_blink_times,
    max_value,
    current_data_index,
    y_max,
):
    ax.clear()

    # Combined RMS
    ax.plot(
        deque_time, deque_rms_combined, label="Combined RMS", color="blue", linewidth=2
    )

    # Blink detection line
    for t in deque_blink_times:
        ax.axvline(x=t, color="red", linewidth=2)

    # Max RMS
    ax.text(
        0.05,
        0.95,
        f"Max RMS: {max_value:.2f}",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.5),
    )

    ax.set_ylim(0, y_max)
    ax.set_xlim(max(0, current_data_index - MAX_DISPLAY_TIME), current_data_index)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("RMS (μV)")
    ax.set_title("Realtime EOG Blink Detection")
    ax.legend(loc="upper right")

    # Update the plot dynamically
    fig.canvas.draw()
    fig.canvas.flush_events()

