#!/usr/bin/awk -f

BEGIN {
  i=0
  win = 0
  n_win = 0
  lambda[0] = 0.0
  back = 0
  temp=330.0
  kT = 0.0019872 * temp 
  beta = 1.0 / (0.0019872 * temp)

  Pass = 1
  ARGV[3] = "Pass=2"
  ARGV[4] = ARGV[1]
  ARGV[5] = ARGV[2]
  ARGC = 6
  Lastlevel = -1
}


(($1 == "#NEW")) {
   if (accumulating) {
       accumulating = 0
       printf "      *** WINDOW %i ENDED UNEXPECTEDLY ***\n", win > "/dev/stderr"
       exit
   }

   l1 = $7
   l2 = $9

   if (l2 > l1) {
      # GOING FORWARD

      if ( back == 0 ) {
          # only if we aren't in the first window
          win++
      }

      back = 0

      if ( l1 != lambda[win - 1]) {
          print "Non-contiguous windows? Going from ", lambda[win - 1], " to ", l1 > "/dev/stderr"
      }

      lambda[win] = l2 

   } else {

      # GOING BACKWARDS

      if (back == 0) {
          # first pass: record number of windows
          n_win = win
      }

      if ( back == 1 ) {
          # only if we aren't in the last window
          win--
      }

      back = 1

      if ( l1 != lambda[win] || l2 != lambda[win - 1] ) {
          printf "Wrong lambda values: got (%f, %f) - expected (%f, %f)\n", l1, l2, lambda[win], lambda[win - 1]
          exit
      }

  }

}

((Pass == 1) && ($1 == "#Free")) {
   i++
   FEP[i] = $12 
}


((Pass ==2) && ($1 == "#STARTING")) {
   accumulating = 1
   nSamples = 0
   xav = 0
   dxav = 0
}


((Pass == 2) && ($1 == "FepEnergy:" && accumulating)) {
   # Accumulating the halved energy differences for SOS
   # xav += exp(- beta * $7 / 2.0)

#   if (nSamples==1) {print "BACK = ", back, "WIN = ", win, "dA = ", FEP[win+n_win*back]}

  if ( back ) {
  xav += 1 / (1 + exp(beta * ($7 + FEP[win])))
  } else {
  xav += 1 / (1 + exp(beta * ($7 - FEP[win])))
  }

   nSamples++
}


# COMPUTE EVERYTHING FOR ONE WINDOW

((Pass == 2) && ($1 == "#Free")) {
   accumulating = 0

#   print "Window = ", win, "dA(FEP) = ", FEP[win], "<.> = ",xav

   xav /= nSamples

   if ( back ) {
       xb[win] = xav
   } else {
       xf[win] = xav
   }

}


END {
  printf "\n%i windows processed.\n", n_win > "/dev/stderr"

  print "# Lambda     A (BAR)       dA  "

  A = 0.0

  printf "%-8s  %9.4f  %9.4f\n", lambda[0], A, 0

  for ( win = 1; win <= n_win; win++ ) {
  xmf = 0.0
  xmb = 0.0

     xmf += xf[win]
     xmb += xb[win]

     dA = FEP[win] - log(xmf / xmb) / beta
     A += dA
     printf "%-8s  %9.4f  %9.4f\n", lambda[win], A, dA
  }

}
