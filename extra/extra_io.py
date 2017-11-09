def break_up_trace(df, duration, peak, channel='primary'):
    sampling = 1/(df.time.iloc[1] - df.time.iloc[0])
    ixs = pace.detect_peaks(df[channel], mph=peak*0.9, mpd=100)

    sweeps = []
    ix_ranges = []
    delta_ix = int((duration/2) * sampling)
    for i, ix in enumerate(ixs):
        ix1 = ix - delta_ix
        ix2 = ix + delta_ix + 1
        ix_ranges.append(np.arange(ix1, ix2))
        sweeps.append('sweep' + str(i+1).zfill(3))

    ars = df.values[np.array(ix_ranges)]
    broken = pd.concat([pd.DataFrame(ar) for ar in ars], keys=sweeps)
    broken.columns = df.columns
    return broken.drop('time', axis=1)
