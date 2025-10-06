from config import MAX_DISPLAY_TIME

def plot_data(
    fig,
    ax,
    all_time,
    all_rms_af7,
    all_rms_af8,
    all_combined_rms,
    blink_times,
    max_value,
    current_time,
    local_y_max,
):
    ax.clear()

    # AF7 and AF8 RMS
    ax.plot(
        all_time,
        all_rms_af7,
        label="RMS AF7",
        color="black",
        linewidth=1,
        alpha=0.3,
    )
    ax.plot(
        all_time,
        all_rms_af8,
        label="RMS AF8",
        color="black",
        linewidth=1,
        alpha=0.3,
    )

    # Combined RMS
    ax.plot(all_time, all_combined_rms, label="Combined RMS", color="blue", linewidth=2)

    # Blink detection line
    first_label = True
    for t in blink_times:
        if first_label:
            ax.axvline(
                x=t,
                color="red",
                linestyle="--",
                linewidth=2,
                label="Blink Detected",
            )
            first_label = False
        else:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=2)

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

    ax.set_ylim(0, local_y_max)
    ax.set_xlim(max(0, current_time - MAX_DISPLAY_TIME), current_time)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("RMS (μV)")
    ax.set_title("Realtime EOG Blink Detection")
    ax.legend(loc="upper right")
    
    fig.canvas.draw()
    fig.canvas.flush_events()