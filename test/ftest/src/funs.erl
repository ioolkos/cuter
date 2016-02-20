-module(funs).
-export([f1/1, f2/3, f3/3, f41/3, f42/3, f5/4, f6/1, f7/2, f8/2,
         f91/3, f92/2, f10/1, f11/3, f12/1]).

-spec f1(fun((integer()) -> integer())) -> ok.
f1(F) ->
  case F(3) of
    42 ->
      case F(10) of
        17 -> error(bug);
        _ -> ok
      end;
    _ -> ok
  end.

-spec f2(fun((integer()) -> integer()), integer(), integer()) -> ok.
f2(F, X, Y) ->
  case F(X) of
    42 ->
      case F(Y) of
        17 -> error(bug);
        _ -> ok
      end;
    _ -> ok
  end.

-spec f3(fun((integer()) -> integer()), integer(), integer()) -> ok.
f3(F, X, Y) ->
  case double(F, X) of
    42 ->
      case double(F, Y) of
       17 -> error(bug);
       _ -> ok
      end;
    _ -> ok
  end.

double(F, X) -> F(F(X)).

-spec f41(fun((integer()) -> any()), integer(), integer()) -> ok.
f41(F, X, Y) ->
  Z = F(X),
  case Z(Y) of
    42 -> error(bug);
    _ -> ok
  end.

-spec f42(fun((integer()) -> any()), integer(), integer()) -> ok.
f42(F, X, Y) ->
  case (catch F(X)) of
    {'EXIT', _} -> ok;
    Z ->
      case Z(Y) of
        42 -> error(bug);
        _ -> ok
      end
  end.

-spec f5(fun((integer(), integer(), integer()) -> integer()), integer(), integer(), integer()) -> ok.
f5(F, X, Y, Z) ->
  case F(X, Y, Z) of
    42 ->
      case F(Z, Y, X) of
        17 -> error(bug);
        _ -> ok
      end;
    _ -> ok
  end.

-spec f6(any()) -> any().
f6(X) when is_function(X, 1) -> f6(X(42));
f6(X) when X =/= 42 -> X.

-spec f7(fun((integer(), integer()) -> integer()), [integer()]) -> integer().
f7(F, L) when is_function(F, 2) ->
  case lists:foldl(F, 0, L) of
    42 -> error(bug);
    R -> R
  end.

-spec f8(fun((any()) -> boolean()), [any()]) -> any().
f8(F, L) when is_function(F, 1) ->
  L1 = lists:filter(F, L),
  hd(L1).

%-spec f91(fun( (any()) -> any()        ), any(), 1) -> any()
%       ; (fun( (any(), any()) -> any() ), any(), 2) -> any().
-spec f91(function(), any(), 1|2) -> any().
f91(F, X, 1) ->
  case F(X) of
    42 -> error(bug);
    R -> R
  end;
f91(F, X, 2) ->
  case F(X, X) of
    42 -> error(bug);
    R -> R
  end.

%-spec f92(fun( (any()) -> any()        ), any()) -> any()
%       ; (fun( (any(), any()) -> any() ), any()) -> any().
-spec f92(function(), any()) -> any().
f92(F, X) when is_function(F, 1) ->
  case F(X) of
    42 -> error(bug);
    R -> R
  end;
f92(F, X) when is_function(F, 2) ->
  case F(X, X) of
    42 -> error(bug);
    R -> R
  end.

-spec f10(function()) -> ok.
f10(F) ->
  G = fun(_) -> 1 end,
  case F(G) of
    42 -> error(bug);
    _ -> ok
  end.

-spec f11(function(), function(), any()) -> any().
f11(F, G, X ) ->
  case (y(F))(X) + (y(G))(X) of
    9 -> error(bug);
    _ -> X
  end.

y(F) ->
  G = fun(H) ->
      F(fun(Z) -> (H(H))(Z) end)
    end,
  G(G).

-spec f12(function()) -> ok.
f12(F) ->
  case (F(fun lists:append/1))(1) of
    42 -> error(bug);
    _ -> ok
  end.
