// Type definitions for javascript-lp-solver

declare module 'javascript-lp-solver' {
  interface Variable {
    [key: string]: any;
  }

  interface Constraint {
    min?: number;
    max?: number;
    equal?: number;
    [key: string]: any;
  }

  interface Model {
    optimize: string;
    opType: 'min' | 'max';
    constraints: { [key: string]: Constraint };
    variables: { [key: string]: Variable };
    ints?: { [key: string]: number };
  }

  interface Solution {
    feasible: boolean;
    result: number;
    bounded: boolean;
    [key: string]: any;
  }

  function Solve(model: Model): Solution;

  export default { Solve };
}
