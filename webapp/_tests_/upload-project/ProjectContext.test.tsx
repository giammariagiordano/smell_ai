import React from "react";
import { renderHook, act } from "@testing-library/react";
import { ProjectProvider, useProjectContext } from "../../context/ProjectContext";

describe("ProjectContext", () => {
  it("should initialize with an empty projects array", () => {
    const { result } = renderHook(() => useProjectContext(), {
      wrapper: ({ children }) => <ProjectProvider>{children}</ProjectProvider>,
    });

    expect(result.current.projects).toEqual([]);
  });

  it("should add a project", () => {
    const { result } = renderHook(() => useProjectContext(), {
      wrapper: ({ children }) => <ProjectProvider>{children}</ProjectProvider>,
    });

    act(() => result.current.addProject());
    expect(result.current.projects.length).toBe(1);
    expect(result.current.projects[0].name).toBe("");
  });

  it("should update a project", () => {
    const { result } = renderHook(() => useProjectContext(), {
      wrapper: ({ children }) => <ProjectProvider>{children}</ProjectProvider>,
    });

    act(() => result.current.addProject());
    act(() =>
      result.current.updateProject(0, { name: "Updated Project", isLoading: true })
    );

    expect(result.current.projects[0].name).toBe("Updated Project");
    expect(result.current.projects[0].isLoading).toBe(true);
  });

  it("should remove a project", () => {
    const { result } = renderHook(() => useProjectContext(), {
      wrapper: ({ children }) => <ProjectProvider>{children}</ProjectProvider>,
    });

    act(() => result.current.addProject());
    act(() => result.current.removeProject(0));

    expect(result.current.projects.length).toBe(0);
  });

it("should throw an error when used outside provider", () => {
  const { result } = renderHook(() => {
    try {
      return useProjectContext();
    } catch (error) {
      return error;
    }
  });

  expect(result.current).toBeInstanceOf(Error);
  expect((result.current as Error).message).toBe(
    "useProjectContext must be used within a ProjectProvider"
    );
});

});
