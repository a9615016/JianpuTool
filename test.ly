\version "2.26.0"

\paper {
  #(set-paper-size "a4")
}

\score {
  \new JianpuStaff {
    \relative c' {
      c4 d e f |
      g g a a |
      g2 |
    }
  }
}